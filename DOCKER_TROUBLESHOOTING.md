# Решение проблем с Docker

## Проблема: Образ Supabase Studio не найден

### Ошибка
```
failed to resolve reference "docker.io/supabase/studio:20240118-7c4c0a4": 
docker.io/supabase/studio:20240118-7c4c0a4: not found
```

### Решение

Образ с указанным тегом больше не доступен в Docker Hub. Обновите `docker-compose.yml`:

#### Вариант 1: Использовать latest (рекомендуется для разработки)
```yaml
supabase_studio:
  image: supabase/studio:latest
```

#### Вариант 2: Использовать конкретную версию
Проверьте доступные теги на [Docker Hub](https://hub.docker.com/r/supabase/studio/tags) и используйте актуальную версию:

```yaml
supabase_studio:
  image: supabase/studio:20231220-0a8b0c5
```

### После обновления

1. Остановите контейнеры:
```bash
docker-compose down
```

2. Удалите старый образ (опционально):
```bash
docker rmi supabase/studio:20240118-7c4c0a4
```

3. Запустите заново:
```bash
docker-compose up -d
```

4. Проверьте логи:
```bash
docker-compose logs supabase_studio
```

## Проверка доступных тегов

### Через Docker Hub веб-интерфейс
1. Перейдите на https://hub.docker.com/r/supabase/studio/tags
2. Найдите актуальный тег
3. Обновите `docker-compose.yml`

### Через командную строку
```bash
# Установите skopeo (если не установлен)
# brew install skopeo  # macOS
# apt-get install skopeo  # Linux

# Проверьте доступные теги
skopeo list-tags docker://supabase/studio | grep -o '"name":"[^"]*"' | cut -d'"' -f4
```

## Другие возможные проблемы

### Проблема: Конфликт версий образов

Если обновляете один образ, убедитесь в совместимости версий всех Supabase сервисов:

- `supabase/postgres` - основная БД
- `supabase/studio` - UI
- `supabase/gotrue` - аутентификация
- `supabase/realtime` - WebSocket
- `supabase/storage-api` - файловое хранилище
- `supabase/postgres-meta` - метаданные

### Проблема: Порт уже занят

Если порт 3001 занят:
```bash
# Проверьте, что использует порт
lsof -i :3001

# Или измените порт в docker-compose.yml
ports:
  - "3002:3000"  # Вместо 3001:3000
```

### Проблема: Недостаточно места на диске

```bash
# Очистите неиспользуемые образы
docker system prune -a

# Очистите volumes (осторожно - удалит данные!)
docker volume prune
```

## Рекомендации

1. **Для разработки**: Используйте `latest` теги для всех сервисов
2. **Для production**: Используйте конкретные версии тегов для стабильности
3. **Регулярно обновляйте**: Проверяйте обновления образов раз в месяц
4. **Делайте бэкапы**: Перед обновлением делайте бэкап данных

## Полезные команды

```bash
# Проверить статус всех сервисов
docker-compose ps

# Просмотр логов конкретного сервиса
docker-compose logs -f supabase_studio

# Перезапуск сервиса
docker-compose restart supabase_studio

# Пересоздание сервиса с новым образом
docker-compose up -d --force-recreate supabase_studio

# Проверить версию образа
docker inspect requirements_supabase_studio | grep Image
```

## Дополнительные ресурсы

- [Supabase Docker Hub](https://hub.docker.com/u/supabase)
- [Supabase Self-Hosting Guide](https://supabase.com/docs/guides/self-hosting/docker)
- [Supabase GitHub Issues](https://github.com/supabase/supabase/issues)

