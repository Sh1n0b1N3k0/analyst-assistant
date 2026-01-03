# Миграция на Supabase + Neo4j

## Обзор изменений

Система была адаптирована для использования Supabase вместо прямого PostgreSQL, сохраняя Neo4j для Graph RAG.

## Что изменилось

### 1. Конфигурация

Supabase + Neo4j**Было:**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/requirements_db
```

**Стало:**
```env
USE_SUPABASE=true
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
```

### 2. Новые модули

- `shared/supabase_config.py` - конфигурация Supabase клиента
- `shared/sync_manager.py` - синхронизация Supabase ↔ Neo4j
- `shared/realtime.py` - Realtime подписки
- `services/requirement_storage/supabase_api.py` - API через Supabase

### 3. Обновленные зависимости

Добавлены:
- `supabase==2.0.3`
- `postgrest==0.13.0`
- `realtime==1.0.0`
- `pgvector==0.2.3`

### 4. Frontend

Добавлен Supabase клиент для Realtime:
- `frontend/src/services/realtime.js`
- Обновлен `frontend/src/services/api.js`

## Преимущества новой архитектуры

1. **Realtime обновления** - автоматические обновления UI при изменении данных
2. **Упрощенное управление** - меньше операционных задач
3. **Встроенный Auth** - можно использовать Supabase Auth
4. **pgvector** - векторный поиск прямо в PostgreSQL
5. **Автоматические бэкапы** - в managed версии Supabase

## Миграция существующих данных

Если у вас уже есть данные в PostgreSQL:

### Вариант 1: Через Supabase Dashboard

1. Экспортируйте данные из старой БД:
```bash
pg_dump -U postgres requirements_db > backup.sql
```

2. Импортируйте в Supabase через SQL Editor

### Вариант 2: Через API

Используйте скрипт миграции:

```python
# migrate_to_supabase.py
from shared.supabase_config import SupabaseClient
from shared.database import SessionLocal
from shared.models import Requirement, Project
import json

supabase = SupabaseClient.get_service_client()
db = SessionLocal()

# Миграция проектов
projects = db.query(Project).all()
for project in projects:
    supabase.table("projects").insert({
        "id": str(project.id),
        "name": project.name,
        # ... другие поля
    }).execute()

# Миграция требований
requirements = db.query(Requirement).all()
for req in requirements:
    supabase.table("requirements").insert({
        "id": str(req.id),
        "project_id": str(req.project_id),
        # ... другие поля
    }).execute()
    
    # Синхронизация с Neo4j
    from shared.sync_manager import sync_manager
    sync_manager.sync_requirement_to_graph(
        req.__dict__,
        str(req.project_id)
    )
```

## Обратная совместимость

Система поддерживает оба режима:

- Если `USE_SUPABASE=true` и настроен Supabase → используется Supabase API
- Иначе → используется обычный PostgreSQL API через SQLAlchemy

Это позволяет:
- Постепенную миграцию
- Использование в разных окружениях
- Fallback на PostgreSQL если Supabase недоступен

## Следующие шаги

1. Создайте проект Supabase
2. Настройте базу данных (см. SUPABASE_SETUP.md)
3. Обновите .env файл
4. Запустите миграцию данных (если есть)
5. Протестируйте систему

## Troubleshooting

### Проблема: "Supabase not available"
- Проверьте переменные окружения
- Убедитесь, что USE_SUPABASE=true
- Проверьте правильность ключей

### Проблема: RLS блокирует запросы
- Используйте Service Role Key для server-side
- Настройте политики RLS (см. SUPABASE_SETUP.md)

### Проблема: Синхронизация с Neo4j не работает
- Проверьте подключение к Neo4j
- Убедитесь, что Neo4j запущен
- Проверьте логи синхронизации

