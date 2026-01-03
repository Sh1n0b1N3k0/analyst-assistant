# Docker конфигурация

## Файлы

- `docker-compose.yml` - Полный стек (Supabase + Neo4j + App)
- `docker-compose.simple.yml` - Упрощенный (PostgreSQL + Neo4j)
- `docker-compose.local.yml` - Минимальный (только БД)
- `docker/kong/kong.yml` - Конфигурация Kong API Gateway

## Использование

### Полный стек

```bash
docker-compose up -d
```

### Упрощенный

```bash
docker-compose -f docker-compose.simple.yml up -d
```

### Только БД

```bash
docker-compose -f docker-compose.local.yml up -d
```

## Порты

- **5432** - PostgreSQL (simple/local)
- **54322** - Supabase PostgreSQL (full stack)
- **7474** - Neo4j HTTP
- **7687** - Neo4j Bolt
- **8000** - Supabase API (Kong)
- **8001** - API Gateway
- **3000** - Frontend
- **3001** - Supabase Studio

