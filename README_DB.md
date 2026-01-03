# Инициализация базы данных

## Описание

Скрипт `init_database.sql` создает полную структуру базы данных для системы управления требованиями на основе ER-диаграммы версии 1.4.1.

## Требования

- PostgreSQL 12+
- Расширения: `uuid-ossp`, `pg_trgm`

## Использование

### Вариант 1: Прямое выполнение SQL

```bash
# Подключение к PostgreSQL
psql -U postgres -d your_database_name

# Выполнение скрипта
\i init_database.sql
```

Или через командную строку:

```bash
psql -U postgres -d your_database_name -f init_database.sql
```

### Вариант 2: Через Python скрипт

```bash
# Установите зависимости
pip install psycopg2-binary

# Настройте config.py с DATABASE_URL
# Например: DATABASE_URL=postgresql://user:password@localhost:5432/requirements_db

# Запустите скрипт
python init_database.py
```

## Создаваемые таблицы

### RBAC (5 таблиц)
- `users` - Пользователи
- `roles` - Роли
- `permissions` - Права доступа
- `user_roles` - Связь пользователей и ролей
- `role_permissions` - Связь ролей и прав

### Основные сущности (3 таблицы)
- `projects` - Проекты
- `requirements` - Требования
- `system_capabilities` - Функции системы

### UI и компоненты (3 таблицы)
- `ui_elements` - Элементы интерфейса
- `system_components` - Системные компоненты
- `component_dependencies` - Зависимости компонентов

### Связи и трассировка (3 таблицы)
- `component_requirement_links` - Реализация требований
- `component_ui_links` - Связь компонентов и UI
- `requirement_relationships` - Связи между требованиями

### Дополнительные функции (10 таблиц)
- `message_broker_details` - Детали брокеров сообщений
- `change_history` - История изменений
- `comments` - Комментарии
- `test_cases` - Тест-кейсы
- `documents` - Документация
- `risks` - Риски
- `metrics` - Метрики
- `external_systems` - Внешние системы
- `deployments` - Развертывание
- `entities` - Сущности системы

### Связи с сущностями (4 таблицы)
- `entity_relationships` - Связи между сущностями
- `requirement_entities` - Связь требований с сущностями
- `component_entities` - Связь компонентов с сущностями
- `ui_entity_links` - Связь UI элементов с сущностями

**Всего: 28 таблиц**

## Индексы

Скрипт создает более 50 индексов для оптимизации запросов:
- Индексы на внешние ключи
- Индексы на часто используемые поля (status, type, etc.)
- GIN индексы для полнотекстового поиска
- GIN индексы для массивов и JSONB

## Триггеры

Автоматическое обновление поля `updated_at` при изменении записей в следующих таблицах:
- users, projects, requirements, system_capabilities
- ui_elements, system_components, message_broker_details
- comments, test_cases, documents, risks
- external_systems, entities

## Начальные данные

Скрипт автоматически создает:
- 5 ролей по умолчанию (admin, analyst, reviewer, developer, viewer)
- 24 права доступа
- Назначение прав ролям

## Представления (Views)

Создаются 3 представления для удобных запросов:
- `requirements_view` - Требования с информацией о пользователях
- `components_health_view` - Компоненты с информацией о здоровье
- `requirement_traceability_view` - Трассировка требований

## Проверка установки

После выполнения скрипта проверьте:

```sql
-- Количество таблиц
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- Должно быть 28 таблиц

-- Проверка ролей
SELECT name, description FROM roles;

-- Проверка прав
SELECT resource_type, action, COUNT(*) as role_count
FROM permissions p
JOIN role_permissions rp ON p.id = rp.permission_id
GROUP BY resource_type, action;
```

## Миграции

Для обновления существующей базы данных используйте инструменты миграций:
- Alembic (рекомендуется)
- Собственные SQL скрипты миграций

## Резервное копирование

Перед выполнением скрипта на production создайте резервную копию:

```bash
pg_dump -U postgres -d your_database_name > backup.sql
```

## Откат изменений

Для полного удаления всех таблиц раскомментируйте секцию DROP TABLE в начале скрипта.

**⚠️ ВНИМАНИЕ: Это удалит все данные!**

## Поддержка

При возникновении проблем проверьте:
1. Версию PostgreSQL (должна быть 12+)
2. Наличие расширений uuid-ossp и pg_trgm
3. Права доступа пользователя базы данных
4. Логи ошибок PostgreSQL

