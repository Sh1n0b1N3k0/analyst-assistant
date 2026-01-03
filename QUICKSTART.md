# Быстрый старт

## Предварительные требования

### Вариант 1: Docker (рекомендуется)

1. Docker и Docker Compose
2. Git

### Вариант 2: Локальная установка

1. Python 3.10+
2. Node.js 18+
3. **Supabase проект** (создайте на https://supabase.com) или локальный Docker
4. Neo4j 5.14+ (или Docker)

## Установка

### 1. Клонирование и настройка окружения

```bash
# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt
```

### 2. Запуск через Docker (рекомендуется)

```bash
# Клонировать репозиторий
git clone <your-repo>
cd analyst-assistant

# Создать .env файл
cp env.example .env
# Отредактировать .env (добавить API ключи)

# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

После запуска будут доступны:
- **Supabase Studio**: http://localhost:3001
- **API Gateway**: http://localhost:8001
- **Frontend**: http://localhost:3000
- **Neo4j Browser**: http://localhost:7474

Подробнее: [DOCKER_SETUP.md](DOCKER_SETUP.md)

### 3. Настройка Supabase (если не используете Docker)

1. Создайте проект на https://supabase.com
2. Получите:
   - Project URL (например: `https://xxxxx.supabase.co`)
   - Anon Key
   - Service Role Key
3. Следуйте инструкциям в [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

#### Neo4j

```bash
# Запустить Neo4j через Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.14
```

Или использовать docker-compose:

```bash
docker-compose up -d postgres neo4j
```

### 4. Настройка переменных окружения (для локальной установки)

Создайте файл `.env`:

```env
# Supabase
USE_SUPABASE=true
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# AI
AI_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

### 5. Инициализация базы данных

Если используете Docker, миграции применятся автоматически.

Для локальной установки:

```bash
# Выполнить миграции в Supabase SQL Editor
# Или использовать скрипт инициализации
# python init_db.py
```

### 6. Запуск Backend (для локальной установки)

```bash
python main.py
```

Backend будет доступен на http://localhost:8000

### 7. Установка и запуск Frontend (для локальной установки)

```bash
cd frontend
npm install
npm run dev
```

Frontend будет доступен на http://localhost:3000

## Использование

### 1. Создание проекта

1. Откройте http://localhost:3000
2. Перейдите в раздел "Проекты"
3. Нажмите "Создать проект"
4. Заполните форму и создайте проект

### 2. Обработка требования

1. Перейдите в раздел "Требования"
2. Нажмите "Обработать требование"
3. Выберите проект и введите неформализованное требование
4. Система автоматически формализует требование

### 3. Анализ в базе знаний

1. Перейдите в раздел "База знаний"
2. Выберите требование для анализа
3. Просмотрите результаты анализа на дубликаты и противоречия

### 4. Генерация спецификации

1. Перейдите в раздел "Спецификации"
2. Выберите требование и тип спецификации
3. Нажмите "Сгенерировать спецификацию"

## API Документация

После запуска backend, документация API доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Структура проекта

```
analyst-assistant/
├── api_gateway/          # API Gateway
├── services/             # Микросервисы
│   ├── project_admin/
│   ├── requirement_processor/
│   ├── knowledge_base/
│   ├── requirement_storage/
│   └── spec_generator/
├── shared/               # Общие модули
├── frontend/             # React UI
└── requirements.txt      # Python зависимости
```

## Troubleshooting

### Проблемы с подключением к БД

- Проверьте, что PostgreSQL запущен
- Проверьте DATABASE_URL в .env

### Проблемы с Neo4j

- Проверьте, что Neo4j запущен
- Проверьте NEO4J_URI и учетные данные

### Проблемы с ИИ агентами

- Проверьте API ключи в .env
- Убедитесь, что выбранный провайдер доступен

