# Настройка Docker для локальной разработки

## Обзор

Проект поддерживает два варианта запуска через Docker:

1. **Полный стек** (`docker-compose.yml`) - все компоненты Supabase + Neo4j
2. **Упрощенный** (`docker-compose.local.yml`) - только PostgreSQL и Neo4j

## Вариант 1: Полный стек Supabase + Neo4j

### Запуск

```bash
# Клонировать репозиторий (если еще не сделано)
git clone <your-repo>
cd analyst-assistant

# Создать файл .env с настройками
cp env.example .env

# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps
```

### Доступные сервисы

После запуска будут доступны:

- **Supabase Studio**: http://localhost:3001 (UI для управления БД)
- **Supabase API**: http://localhost:8000
- **API Gateway**: http://localhost:8001
- **Frontend**: http://localhost:3000
- **Neo4j Browser**: http://localhost:7474
- **Neo4j Bolt**: bolt://localhost:7687

### Переменные окружения

Создайте файл `.env`:

```env
# Supabase
POSTGRES_PASSWORD=your-super-secret-jwt-token-with-at-least-32-characters-long
JWT_SECRET=your-super-secret-jwt-token-with-at-least-32-characters-long
ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0
SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU

# Neo4j
NEO4J_PASSWORD=password

# AI
AI_PROVIDER=openai
OPENAI_API_KEY=your-key-here
```

### Инициализация базы данных

После первого запуска выполните миграции:

```bash
# Подключиться к Supabase PostgreSQL
docker exec -it requirements_supabase_db psql -U supabase_admin -d postgres

# Выполнить миграцию схемы prompts
\i /docker-entrypoint-initdb.d/create_prompts_schema.sql
```

Или через Supabase Studio:
1. Откройте http://localhost:3001
2. Перейдите в SQL Editor
3. Выполните SQL из `migrations/create_prompts_schema.sql`

## Вариант 2: Упрощенный (только PostgreSQL + Neo4j)

Для быстрой разработки без всех компонентов Supabase:

```bash
# Запустить только БД
docker-compose -f docker-compose.simple.yml up -d

# Настроить .env для прямого подключения к PostgreSQL
USE_SUPABASE=false
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/requirements_db
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## Вариант 3: Минимальный (только БД)

Для запуска только баз данных без приложения:

```bash
docker-compose -f docker-compose.local.yml up -d
```

## Полезные команды

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f supabase_db
docker-compose logs -f neo4j
docker-compose logs -f api_gateway
```

### Остановка сервисов

```bash
# Остановить все
docker-compose down

# Остановить и удалить volumes (удалит данные!)
docker-compose down -v
```

### Перезапуск сервиса

```bash
docker-compose restart api_gateway
```

### Подключение к БД

```bash
# Supabase PostgreSQL (полный стек)
docker exec -it requirements_supabase_db psql -U supabase_admin -d postgres

# PostgreSQL (упрощенный)
docker exec -it requirements_postgres psql -U postgres -d requirements_db

# Neo4j Cypher Shell
docker exec -it requirements_neo4j cypher-shell -u neo4j -p password

# Neo4j Browser
# Откройте http://localhost:7474 в браузере
# Логин: neo4j
# Пароль: password
```

### Очистка

```bash
# Удалить все контейнеры и volumes
docker-compose down -v

# Удалить все образы проекта
docker-compose down --rmi all
```

## Troubleshooting

### Проблема: Порт уже занят

Если порт занят, измените в `docker-compose.yml`:

```yaml
ports:
  - "5433:5432"  # Вместо 5432
```

### Проблема: Supabase не запускается

1. Проверьте логи: `docker-compose logs supabase_db`
2. Убедитесь, что пароль достаточно длинный (минимум 32 символа)
3. Проверьте доступность портов
4. Убедитесь, что все зависимости запущены: `docker-compose ps`

### Проблема: Kong не запускается

1. Проверьте, что файл `docker/kong/kong.yml` существует
2. Проверьте логи: `docker-compose logs kong`
3. Убедитесь, что все сервисы Supabase запущены

### Проблема: Neo4j не подключается

1. Проверьте логи: `docker-compose logs neo4j`
2. Убедитесь, что пароль правильный
3. Проверьте, что порты 7474 и 7687 свободны

### Проблема: Миграции не применяются

1. Проверьте, что файлы миграций в правильной директории
2. Выполните миграции вручную через SQL Editor
3. Проверьте права доступа к файлам

## Структура сервисов

```
┌─────────────────────────────────────┐
│         Supabase Stack              │
│  ┌─────────┐  ┌─────────┐          │
│  │   DB    │  │  Studio │          │
│  └────┬────┘  └─────────┘          │
│       │                             │
│  ┌────▼────┐  ┌─────────┐          │
│  │ PostgREST│  │  Auth   │          │
│  └────┬────┘  └─────────┘          │
│       │                             │
│  ┌────▼────┐                       │
│  │   Kong  │ (API Gateway)         │
│  └─────────┘                       │
└─────────────────────────────────────┘
         │
         │
┌────────▼────────────────────────────┐
│         Neo4j                       │
│    (Graph Database)                 │
└─────────────────────────────────────┘
         │
         │
┌────────▼────────────────────────────┐
│    Application Services             │
│  - API Gateway                      │
│  - Frontend                         │
└─────────────────────────────────────┘
```

## Production

Для production используйте:
- Управляемый Supabase (supabase.com)
- Управляемый Neo4j Aura
- Или self-hosted версии с правильной настройкой безопасности

## Дополнительные ресурсы

- [Supabase Local Development](https://supabase.com/docs/guides/cli/local-development)
- [Neo4j Docker](https://neo4j.com/docs/operations-manual/current/docker/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

