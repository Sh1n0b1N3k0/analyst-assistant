# Настройка хранилища промптов в Supabase

## Обзор

Промпты хранятся в отдельной схеме `prompts` в Supabase для:
- Персистентного хранения
- Версионирования
- Синхронизации между инстансами
- Управления через UI
- Аудита изменений

## Шаг 1: Создание схемы

### Вариант 1: Через SQL Editor

1. Откройте Supabase Dashboard
2. Перейдите в SQL Editor
3. Выполните SQL из файла `migrations/create_prompts_schema.sql`

### Вариант 2: Через миграцию

```sql
-- Создать схему
CREATE SCHEMA IF NOT EXISTS prompts;

-- Создать таблицу
CREATE TABLE IF NOT EXISTS prompts.prompts (
    id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    agent_type TEXT NOT NULL,
    prompt_type TEXT NOT NULL,
    template TEXT NOT NULL,
    variables JSONB DEFAULT '[]'::jsonb,
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, version)
);
```

## Шаг 2: Создание индексов

```sql
-- Индексы для быстрого поиска
CREATE INDEX idx_prompts_agent_type ON prompts.prompts(agent_type);
CREATE INDEX idx_prompts_prompt_type ON prompts.prompts(prompt_type);
CREATE INDEX idx_prompts_agent_prompt_type ON prompts.prompts(agent_type, prompt_type);
CREATE INDEX idx_prompts_active ON prompts.prompts(is_active) WHERE is_active = true;
CREATE INDEX idx_prompts_version ON prompts.prompts(id, version DESC);
```

## Шаг 3: Настройка Row Level Security (RLS)

```sql
-- Включить RLS
ALTER TABLE prompts.prompts ENABLE ROW LEVEL SECURITY;

-- Политика: все могут читать активные промпты
CREATE POLICY "Anyone can read active prompts"
ON prompts.prompts
FOR SELECT
USING (is_active = true);

-- Политика: только service role может изменять промпты
-- (настраивается через Supabase Dashboard или используйте service key)
```

## Шаг 4: Создание функций

### Функция для получения последней версии промпта

```sql
CREATE OR REPLACE FUNCTION prompts.get_latest_prompt(prompt_id TEXT)
RETURNS TABLE (
    id TEXT,
    name TEXT,
    description TEXT,
    agent_type TEXT,
    prompt_type TEXT,
    template TEXT,
    variables JSONB,
    version INTEGER,
    is_active BOOLEAN,
    metadata JSONB,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, p.description, p.agent_type, p.prompt_type, 
           p.template, p.variables, p.version, p.is_active, p.metadata,
           p.created_at, p.updated_at
    FROM prompts.prompts p
    WHERE p.id = prompt_id
      AND p.is_active = true
    ORDER BY p.version DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;
```

### Функция для получения промптов агента

```sql
CREATE OR REPLACE FUNCTION prompts.get_agent_prompts(
    agent_type_param TEXT,
    prompt_type_param TEXT DEFAULT NULL
)
RETURNS TABLE (
    id TEXT,
    name TEXT,
    description TEXT,
    agent_type TEXT,
    prompt_type TEXT,
    template TEXT,
    variables JSONB,
    version INTEGER,
    is_active BOOLEAN,
    metadata JSONB,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (p.id)
           p.id, p.name, p.description, p.agent_type, p.prompt_type,
           p.template, p.variables, p.version, p.is_active, p.metadata,
           p.created_at, p.updated_at
    FROM prompts.prompts p
    WHERE p.agent_type = agent_type_param
      AND p.is_active = true
      AND (prompt_type_param IS NULL OR p.prompt_type = prompt_type_param)
    ORDER BY p.id, p.version DESC;
END;
$$ LANGUAGE plpgsql;
```

## Шаг 5: Автоматическая загрузка промптов по умолчанию

Промпты по умолчанию загружаются автоматически при первом запуске системы, если таблица пуста.

Или можно загрузить вручную через API:

```bash
# Промпты загрузятся автоматически при первом обращении к API
curl http://localhost:8000/api/prompts
```

## Шаг 6: Проверка работы

### Проверить схему

```sql
-- Проверить существование схемы
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'prompts';

-- Проверить таблицу
SELECT * FROM prompts.prompts LIMIT 5;
```

### Проверить через API

```bash
# Получить список промптов
curl http://localhost:8000/api/prompts

# Получить промпт для агента
curl http://localhost:8000/api/prompts/agent/project_admin/type/analysis
```

## Структура таблицы

| Колонка | Тип | Описание |
|---------|-----|----------|
| `id` | TEXT | Уникальный идентификатор промпта |
| `name` | TEXT | Название промпта |
| `description` | TEXT | Описание назначения |
| `agent_type` | TEXT | Тип агента (project_admin, requirement_processor, etc.) |
| `prompt_type` | TEXT | Тип промпта (analysis, formalization, etc.) |
| `template` | TEXT | Шаблон промпта с переменными {variable} |
| `variables` | JSONB | Массив переменных в шаблоне |
| `version` | INTEGER | Версия промпта |
| `is_active` | BOOLEAN | Активен ли промпт |
| `metadata` | JSONB | Дополнительные метаданные |
| `created_at` | TIMESTAMPTZ | Дата создания |
| `updated_at` | TIMESTAMPTZ | Дата обновления |

## Версионирование

При обновлении промпта создается новая запись с:
- Тем же `id`
- Увеличенным `version`
- Обновленным `updated_at`

Старые версии сохраняются для истории и возможного отката.

## Миграция существующих промптов

Если у вас уже есть промпты в in-memory хранилище:

```python
from shared.prompt_store import PromptStore
from shared.prompt_store_supabase import SupabasePromptStore

# Получить промпты из старого хранилища
old_store = PromptStore()
old_prompts = old_store.list_prompts()

# Загрузить в Supabase
new_store = SupabasePromptStore()
for prompt in old_prompts:
    new_store.add_prompt(prompt)
```

## Troubleshooting

### Проблема: "Schema prompts does not exist"
- Выполните миграцию из `migrations/create_prompts_schema.sql`
- Проверьте права доступа к созданию схем

### Проблема: "Permission denied"
- Убедитесь, что используете Service Role Key для записи
- Проверьте политики RLS

### Проблема: Промпты не загружаются
- Проверьте подключение к Supabase
- Проверьте логи ошибок
- Убедитесь, что таблица существует

### Проблема: Версионирование не работает
- Проверьте, что PRIMARY KEY включает (id, version)
- Убедитесь, что версия увеличивается при обновлении

## Best Practices

1. **Используйте отдельную схему** - изоляция данных промптов
2. **Версионирование** - всегда создавайте новую версию при изменении
3. **RLS политики** - настройте правильные политики доступа
4. **Индексы** - используйте индексы для быстрого поиска
5. **Метаданные** - храните дополнительные настройки в metadata

## Дополнительные возможности

### Просмотр истории версий

```sql
-- Получить все версии промпта
SELECT * FROM prompts.prompts 
WHERE id = 'project_admin_analyze' 
ORDER BY version DESC;
```

### Откат к предыдущей версии

```sql
-- Деактивировать текущую версию
UPDATE prompts.prompts 
SET is_active = false 
WHERE id = 'project_admin_analyze' AND version = 3;

-- Активировать предыдущую версию
UPDATE prompts.prompts 
SET is_active = true 
WHERE id = 'project_admin_analyze' AND version = 2;
```

### Статистика использования

```sql
-- Количество промптов по агентам
SELECT agent_type, COUNT(DISTINCT id) as prompt_count
FROM prompts.prompts
WHERE is_active = true
GROUP BY agent_type;
```

