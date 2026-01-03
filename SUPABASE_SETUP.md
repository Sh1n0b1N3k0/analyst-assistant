# Настройка Supabase для системы управления требованиями

## Шаг 1: Создание проекта Supabase

1. Перейдите на https://supabase.com
2. Создайте новый проект
3. Запишите:
   - Project URL (например: `https://xxxxx.supabase.co`)
   - Anon Key (публичный ключ)
   - Service Role Key (приватный ключ для server-side)

## Шаг 2: Настройка базы данных

### Включение расширений

В SQL Editor Supabase выполните:

```sql
-- Включить pgvector для векторного поиска
CREATE EXTENSION IF NOT EXISTS vector;

-- Включить UUID расширение
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Создание таблиц

Таблицы будут созданы на основе ER-диаграммы. Основные таблицы:

- `projects` - проекты
- `requirements` - требования
- `users` - пользователи
- `entities` - сущности системы
- `entity_relationships` - связи между сущностями
- И другие таблицы из ER_Main.wsd

## Шаг 3: Настройка Row Level Security (RLS)

### Политики для таблицы requirements

```sql
-- Включить RLS
ALTER TABLE requirements ENABLE ROW LEVEL SECURITY;

-- Политика: пользователи могут читать требования своего проекта
CREATE POLICY "Users can read requirements of their projects"
ON requirements
FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM project_members pm
    WHERE pm.project_id = requirements.project_id
    AND pm.user_id = auth.uid()
  )
);

-- Политика: пользователи могут создавать требования в своих проектах
CREATE POLICY "Users can create requirements in their projects"
ON requirements
FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM project_members pm
    WHERE pm.project_id = requirements.project_id
    AND pm.user_id = auth.uid()
  )
);
```

### Политики для таблицы projects

```sql
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Владелец проекта может управлять проектом
CREATE POLICY "Project owners can manage their projects"
ON projects
FOR ALL
USING (owner_id = auth.uid());
```

## Шаг 4: Настройка Realtime

В Supabase Dashboard:
1. Перейдите в Settings → API
2. Включите Realtime для нужных таблиц:
   - `requirements`
   - `projects`
   - `entities`

Или через SQL:

```sql
-- Включить Realtime для таблицы requirements
ALTER PUBLICATION supabase_realtime ADD TABLE requirements;

ALTER PUBLICATION supabase_realtime ADD TABLE projects;
```

## Шаг 5: Настройка переменных окружения

Создайте файл `.env`:

```env
# Supabase
USE_SUPABASE=true
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Опционально: прямой connection string для SQLAlchemy
SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres

# Neo4j (остается отдельно)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# AI Configuration
AI_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

## Шаг 6: Создание таблицы синхронизации (опционально)

Для отслеживания синхронизации с Neo4j:

```sql
CREATE TABLE IF NOT EXISTS requirement_sync_status (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  requirement_id UUID REFERENCES requirements(id) ON DELETE CASCADE,
  synced_to_graph BOOLEAN DEFAULT false,
  synced_at TIMESTAMPTZ,
  graph_node_id TEXT,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sync_status_requirement ON requirement_sync_status(requirement_id);
CREATE INDEX idx_sync_status_synced ON requirement_sync_status(synced_to_graph);
```

## Шаг 7: Настройка схемы для промптов

Создайте отдельную схему для хранения промптов ИИ агентов:

```sql
-- Выполнить миграцию из migrations/create_prompts_schema.sql
-- Или следовать инструкциям в SUPABASE_PROMPTS_SETUP.md
```

Подробные инструкции: [SUPABASE_PROMPTS_SETUP.md](SUPABASE_PROMPTS_SETUP.md)

## Шаг 8: Настройка функций для автоматической синхронизации

Можно создать функцию для автоматической синхронизации при изменении требования:

```sql
-- Функция для логирования изменений (для синхронизации)
CREATE OR REPLACE FUNCTION log_requirement_change()
RETURNS TRIGGER AS $$
BEGIN
  -- Обновить статус синхронизации
  INSERT INTO requirement_sync_status (requirement_id, synced_to_graph, synced_at)
  VALUES (NEW.id, false, NOW())
  ON CONFLICT (requirement_id) 
  DO UPDATE SET 
    synced_to_graph = false,
    synced_at = NOW(),
    updated_at = NOW();
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для автоматического логирования
CREATE TRIGGER requirement_change_trigger
AFTER INSERT OR UPDATE ON requirements
FOR EACH ROW
EXECUTE FUNCTION log_requirement_change();
```

## Шаг 8: Настройка векторного поиска (pgvector)

### Создание таблицы для embeddings

```sql
-- Таблица для хранения векторных представлений требований
CREATE TABLE IF NOT EXISTS requirement_embeddings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  requirement_id UUID REFERENCES requirements(id) ON DELETE CASCADE,
  embedding vector(1536), -- Размерность зависит от модели (OpenAI = 1536)
  model TEXT DEFAULT 'text-embedding-ada-002',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(requirement_id)
);

-- Индекс для векторного поиска
CREATE INDEX ON requirement_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Функция для поиска похожих требований

```sql
CREATE OR REPLACE FUNCTION find_similar_requirements(
  query_embedding vector(1536),
  similarity_threshold float DEFAULT 0.8,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  requirement_id UUID,
  similarity float,
  name TEXT,
  shall TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    re.requirement_id,
    1 - (re.embedding <=> query_embedding) as similarity,
    r.name,
    r.shall
  FROM requirement_embeddings re
  JOIN requirements r ON r.id = re.requirement_id
  WHERE 1 - (re.embedding <=> query_embedding) > similarity_threshold
  ORDER BY re.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

## Шаг 9: Миграция данных (если есть существующие данные)

Если у вас уже есть данные в PostgreSQL:

1. Экспортируйте данные из старой БД
2. Импортируйте в Supabase через SQL Editor или API
3. Запустите синхронизацию с Neo4j

## Шаг 10: Тестирование

1. Проверьте подключение:
```python
from shared.supabase_config import SupabaseClient

client = SupabaseClient.get_client()
if client:
    print("Supabase connected!")
```

2. Проверьте Realtime:
```python
from shared.realtime import realtime_manager

def callback(payload):
    print("Update received:", payload)

realtime_manager.subscribe_to_projects(callback)
```

## Полезные ссылки

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase/supabase-py)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Supabase Realtime](https://supabase.com/docs/guides/realtime)

## Troubleshooting

### Проблема: "Supabase not available"
- Проверьте SUPABASE_URL и SUPABASE_KEY в .env
- Убедитесь, что ключи правильные

### Проблема: RLS блокирует запросы
- Проверьте политики RLS
- Используйте Service Role Key для server-side операций

### Проблема: Realtime не работает
- Убедитесь, что Realtime включен для таблиц
- Проверьте настройки в Supabase Dashboard

### Проблема: Векторный поиск медленный
- Увеличьте количество lists в индексе
- Проверьте размерность векторов

