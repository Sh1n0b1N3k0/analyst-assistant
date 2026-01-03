# Тестирование

## Обзор

Проект включает unit и integration тесты для проверки функциональности системы.

## Структура тестов

```
tests/
├── __init__.py
├── conftest.py              # Конфигурация pytest и фикстуры
├── test_exceptions.py       # Тесты обработки исключений
├── test_security.py         # Тесты безопасности (JWT, пароли)
├── test_retry.py            # Тесты retry логики
├── test_api_integration.py  # Integration тесты API
└── test_graph_rag.py        # Тесты Graph RAG
```

## Запуск тестов

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск всех тестов

```bash
pytest
```

### Запуск с покрытием кода

```bash
pytest --cov=shared --cov=services --cov=api_gateway --cov-report=html
```

### Запуск конкретного теста

```bash
pytest tests/test_security.py
```

### Запуск с подробным выводом

```bash
pytest -v
```

## Типы тестов

### Unit тесты

- `test_exceptions.py` - тесты кастомных исключений
- `test_security.py` - тесты JWT токенов и хеширования паролей
- `test_retry.py` - тесты retry логики
- `test_graph_rag.py` - тесты Graph RAG (с моками)

### Integration тесты

- `test_api_integration.py` - тесты API endpoints, middleware, headers

## Фикстуры

В `conftest.py` определены общие фикстуры:

- `mock_env_vars` - мокирование переменных окружения
- `sample_requirement_data` - пример данных требования
- `sample_project_data` - пример данных проекта

## Покрытие кода

Цель: минимум 70% покрытия кода тестами.

Текущее покрытие можно проверить:

```bash
pytest --cov --cov-report=term-missing
```

## Добавление новых тестов

1. Создайте файл `test_<module_name>.py` в директории `tests/`
2. Используйте фикстуры из `conftest.py`
3. Следуйте naming convention: `test_<functionality>`
4. Добавьте docstrings для описания тестов

## Пример теста

```python
def test_example_functionality(client):
    """Тест функциональности."""
    response = client.get("/api/endpoint")
    
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

## CI/CD

Тесты должны проходить в CI/CD pipeline перед деплоем.

Для запуска в CI:

```bash
pytest --cov --cov-report=xml
```

