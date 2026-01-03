# Руководство по безопасности

## Обзор

Документ описывает реализованные меры безопасности и рекомендации по настройке.

## Реализованные меры безопасности

### 1. JWT Аутентификация

Система использует JWT токены для аутентификации пользователей.

**Настройка:**
```env
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Использование:**
```python
from shared.security import get_current_user, create_access_token

# Создание токена
token = create_access_token({"sub": "user-id", "email": "user@example.com"})

# Защита endpoint
@app.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    return {"user_id": user["user_id"]}
```

### 2. Хеширование паролей

Пароли хешируются с использованием bcrypt.

```python
from shared.security import get_password_hash, verify_password

# Хеширование
hashed = get_password_hash("plain_password")

# Проверка
is_valid = verify_password("plain_password", hashed)
```

### 3. CORS (Cross-Origin Resource Sharing)

Настроен безопасный CORS с указанием разрешенных источников.

**Настройка:**
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

**В production:**
- Укажите конкретные домены
- Не используйте `*` для `allow_origins`
- Настройте `allow_credentials` только при необходимости

### 4. Rate Limiting

Реализован rate limiting для защиты от DDoS и злоупотреблений.

**Настройка:**
```env
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_REQUESTS_PER_HOUR=1000
```

**Заголовки ответа:**
- `X-RateLimit-Limit-Minute` - лимит в минуту
- `X-RateLimit-Remaining-Minute` - оставшиеся запросы
- `X-RateLimit-Limit-Hour` - лимит в час
- `X-RateLimit-Remaining-Hour` - оставшиеся запросы

### 5. Security Headers

Добавлены security headers для защиты от различных атак:

- `X-Content-Type-Options: nosniff` - защита от MIME sniffing
- `X-Frame-Options: DENY` - защита от clickjacking
- `X-XSS-Protection: 1; mode=block` - защита от XSS
- `Strict-Transport-Security` - принудительное использование HTTPS

### 6. Обработка ошибок

Реализована безопасная обработка ошибок без утечки информации:

- Кастомные исключения с контролируемыми сообщениями
- Логирование ошибок без раскрытия чувствительных данных
- Структурированные ответы об ошибках

## Рекомендации для Production

### 1. Секретные ключи

- **НЕ** храните секретные ключи в коде
- Используйте переменные окружения или secret management (AWS Secrets Manager, HashiCorp Vault)
- Регулярно ротируйте секретные ключи
- Используйте разные ключи для разных окружений

### 2. HTTPS

- Всегда используйте HTTPS в production
- Настройте SSL/TLS сертификаты
- Используйте HSTS (Strict-Transport-Security)

### 3. База данных

- Используйте connection pooling
- Настройте RLS (Row Level Security) в Supabase
- Регулярно делайте бэкапы
- Используйте отдельные пользователи БД с минимальными правами

### 4. API Keys

- Храните API ключи (OpenAI, Anthropic) в безопасном месте
- Используйте разные ключи для разных окружений
- Регулярно ротируйте ключи
- Мониторьте использование ключей

### 5. Мониторинг и логирование

- Настройте централизованное логирование
- Мониторьте подозрительную активность
- Настройте алерты на аномалии
- Регулярно просматривайте логи на предмет утечек данных

### 6. Аутентификация и авторизация

- Реализуйте RBAC (Role-Based Access Control)
- Используйте refresh tokens для долгоживущих сессий
- Реализуйте 2FA (двухфакторная аутентификация) для критичных операций
- Настройте session timeout

### 7. Валидация входных данных

- Всегда валидируйте входные данные
- Используйте Pydantic модели для валидации
- Санитизируйте пользовательский ввод
- Защищайтесь от SQL injection (используйте параметризованные запросы)

### 8. Зависимости

- Регулярно обновляйте зависимости
- Проверяйте уязвимости (например, `pip-audit`, `safety`)
- Используйте только проверенные библиотеки

## Проверка безопасности

### Статический анализ

```bash
# Проверка уязвимостей в зависимостях
pip-audit

# Проверка безопасности кода
bandit -r . -f json
```

### Тестирование

Запустите тесты безопасности:

```bash
pytest tests/test_security.py -v
```

## Инциденты безопасности

В случае обнаружения уязвимости:

1. Немедленно исправьте уязвимость
2. Оцените масштаб проблемы
3. Уведомите затронутых пользователей
4. Обновите документацию
5. Рассмотрите возможность security audit

## Дополнительные ресурсы

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Supabase Security](https://supabase.com/docs/guides/platform/security)

