# Система управления требованиями к программному обеспечению

Комплексная система для управления требованиями к программному обеспечению с использованием ИИ агентов, Graph RAG и автоматической генерацией спецификаций.

## Архитектура

Система состоит из 5 основных компонентов:

1. **Администратор проекта** - управление проектами с ИИ агентом
2. **Обработчик входящих требований** - формализация требований с ИИ агентом
3. **База знаний требований** - Graph RAG с проверкой дублей и противоречий
4. **Хранилище требований** - реляционная БД для хранения всех данных
5. **Генератор спецификаций** - автоматическая генерация различных типов спецификаций

## Технологический стек

### Backend
- FastAPI
- **Supabase** (PostgreSQL + Realtime + Auth)
- **Neo4j** (Graph RAG)
- SQLAlchemy (опционально, для прямого доступа к PostgreSQL)
- LangChain
- OpenAI/Anthropic
- pgvector (векторный поиск в Supabase)

### Frontend
- React
- Material-UI
- React Router
- Axios

## Установка

### Требования
- Python 3.10+
- Node.js 18+
- **Supabase проект** (или PostgreSQL 15+ для self-hosted)
- Neo4j 5.14+

### Backend

```bash
# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp env.example .env
# Отредактировать .env файл
# Укажите SUPABASE_URL и SUPABASE_KEY из вашего Supabase проекта

# Запустить миграции БД
# TODO: добавить команду для инициализации БД
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker Compose (рекомендуется)

```bash
# Создать .env файл
cp env.example .env

# Запустить все сервисы (Supabase + Neo4j + App)
docker-compose up -d

# Проверить статус
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

После запуска:
- **Supabase Studio**: http://localhost:3001
- **API Gateway**: http://localhost:8001
- **Frontend**: http://localhost:3000
- **Neo4j Browser**: http://localhost:7474

Подробнее: [DOCKER_SETUP.md](DOCKER_SETUP.md)

## Конфигурация

Создайте файл `.env` на основе `.env.example`:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/requirements_db

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# AI Configuration
AI_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

## Запуск

### Backend
```bash
python main.py
```

### Frontend
```bash
cd frontend
npm run dev
```

Система будет доступна:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Использование

1. **Создание проекта**: Используйте "Администратор проекта" для создания нового проекта
2. **Обработка требований**: Загрузите неформализованные требования через "Обработчик требований"
3. **Анализ**: Используйте "Базу знаний" для проверки дублей и противоречий
4. **Генерация спецификаций**: Создавайте спецификации через "Генератор спецификаций"

## Документация

- [Быстрый старт](QUICKSTART.md)
- [Настройка Docker](DOCKER_SETUP.md)
- [Архитектура системы](SYSTEM_ARCHITECTURE.md)
- [Сравнение архитектур](ARCHITECTURE_COMPARISON.md)
- [Настройка Supabase](SUPABASE_SETUP.md)
- [Настройка хранилища промптов в Supabase](SUPABASE_PROMPTS_SETUP.md)
- [Настройка ИИ моделей](AI_CONFIG_GUIDE.md)
- [Хранилище промптов](PROMPT_STORE_GUIDE.md)
- [ER-диаграмма](ER_Main.wsd)

## Лицензия

MIT

