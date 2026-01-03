# Руководство по хранилищу промптов

## Обзор

Хранилище промптов позволяет управлять промптами для ИИ агентов централизованно. Это дает возможность:
- Версионировать промпты
- Тестировать разные версии промптов
- Управлять промптами через API
- Использовать разные промпты для разных сценариев

## Хранение

Промпты хранятся в **отдельной схеме `prompts` в Supabase** для:
- Персистентного хранения
- Версионирования
- Синхронизации между инстансами
- Управления через UI
- Аудита изменений

Если Supabase недоступен, используется in-memory хранилище.

**Настройка Supabase**: См. [SUPABASE_PROMPTS_SETUP.md](SUPABASE_PROMPTS_SETUP.md)

## Структура промпта

```json
{
  "id": "prompt_id",
  "name": "Название промпта",
  "description": "Описание назначения",
  "agent_type": "project_admin|requirement_processor|knowledge_base|spec_generator",
  "prompt_type": "analysis|formalization|duplicate_analysis|conflict_analysis|user_story|rest_api",
  "template": "Шаблон с переменными {variable}",
  "variables": ["variable1", "variable2"],
  "version": 1,
  "is_active": true,
  "metadata": {"temperature": 0.7},
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

## API Endpoints

### Получить список промптов

```http
GET /api/prompts?agent_type=project_admin&prompt_type=analysis
```

### Получить промпт по ID

```http
GET /api/prompts/{prompt_id}
```

### Получить активный промпт для агента

```http
GET /api/prompts/agent/{agent_type}/type/{prompt_type}
```

### Создать новый промпт

```http
POST /api/prompts
Content-Type: application/json

{
  "name": "Новый промпт",
  "description": "Описание",
  "agent_type": "project_admin",
  "prompt_type": "analysis",
  "template": "Анализируй проект: {project_data}",
  "variables": ["project_data"],
  "is_active": true
}
```

### Обновить промпт (создает новую версию)

```http
PUT /api/prompts/{prompt_id}
Content-Type: application/json

{
  "template": "Обновленный шаблон: {project_data}",
  "variables": ["project_data"]
}
```

### Отрендерить промпт

```http
POST /api/prompts/render
Content-Type: application/json

{
  "prompt_id": "project_admin_analyze",
  "variables": {
    "project_data": "{\"name\": \"Проект\"}"
  }
}
```

### Деактивировать промпт

```http
DELETE /api/prompts/{prompt_id}
```

## Типы промптов по агентам

### Project Admin

- `analysis` - Анализ проекта и генерация рекомендаций

### Requirement Processor

- `formalization` - Формализация неформализованного требования

### Knowledge Base

- `duplicate_analysis` - Анализ дубликатов требований
- `conflict_analysis` - Анализ противоречий
- `recommendations` - Генерация рекомендаций
- `completeness` - Анализ полноты требований

### Spec Generator

- `user_story` - Генерация User Story
- `use_case` - Генерация Use Case
- `rest_api` - Генерация REST API (OpenAPI)
- `grpc_api` - Генерация gRPC API
- `async_api` - Генерация AsyncAPI
- `uml_sequence` - Генерация UML Sequence диаграммы
- `uml_er` - Генерация UML ER диаграммы
- `c4_context` - Генерация C4 Context диаграммы

## Примеры использования

### Пример 1: Создание кастомного промпта для анализа проекта

```python
import requests

prompt_data = {
    "name": "Расширенный анализ проекта",
    "description": "Промпт с дополнительными рекомендациями",
    "agent_type": "project_admin",
    "prompt_type": "analysis",
    "template": """You are an expert project manager.

Analyze the project and provide:
1. Detailed recommendations
2. Risk assessment
3. Team structure suggestions
4. Timeline recommendations

Project: {project_data}

Return JSON with all recommendations.""",
    "variables": ["project_data"],
    "is_active": True
}

response = requests.post("http://localhost:8000/api/prompts", json=prompt_data)
print(response.json())
```

### Пример 2: Обновление промпта

```python
import requests

# Обновление создает новую версию
updates = {
    "template": "Обновленный шаблон: {project_data}\nДополнительные инструкции...",
    "metadata": {"temperature": 0.8}
}

response = requests.put(
    "http://localhost:8000/api/prompts/project_admin_analyze",
    json=updates
)
print(response.json())
```

### Пример 3: Тестирование промпта

```python
import requests

# Отрендерить промпт с тестовыми данными
render_request = {
    "prompt_id": "project_admin_analyze",
    "variables": {
        "project_data": '{"name": "Test Project", "methodology": "Agile"}'
    }
}

response = requests.post(
    "http://localhost:8000/api/prompts/render",
    json=render_request
)
print(response.json()["rendered"])
```

### Пример 4: Использование в коде

```python
from shared.prompt_store import prompt_store

# Получить активный промпт
prompt = prompt_store.get_active_prompt("project_admin", "analysis")

# Отрендерить с переменными
rendered = prompt_store.render_prompt(
    prompt.id,
    {"project_data": json.dumps(project_data)}
)
```

## Версионирование

При обновлении промпта создается новая версия:
- Старая версия сохраняется
- Новая версия получает увеличенный номер версии
- Активной остается последняя версия

## Миграция на хранилище промптов

Агенты автоматически используют промпты из хранилища, если они доступны. Если промпт не найден, используется встроенный fallback промпт.

Это позволяет:
1. Постепенно мигрировать на хранилище промптов
2. Тестировать новые промпты без изменения кода
3. Откатываться к старым версиям при необходимости

## Best Practices

1. **Именование**: Используйте понятные имена для промптов
2. **Версионирование**: Всегда создавайте новую версию при изменении
3. **Тестирование**: Тестируйте промпты через `/api/prompts/render` перед активацией
4. **Документация**: Описывайте переменные и их назначение
5. **Метаданные**: Используйте metadata для хранения дополнительных настроек

## Интеграция с Supabase (будущее)

В будущем можно хранить промпты в Supabase для:
- Персистентного хранения
- Синхронизации между инстансами
- Управления через UI
- Аудит изменений

