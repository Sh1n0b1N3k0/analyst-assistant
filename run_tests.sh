#!/bin/bash
# Скрипт для запуска тестов

set -e

echo "=========================================="
echo "Запуск тестов Analyst Assistant"
echo "=========================================="

# Проверка виртуального окружения
if [ -d "venv" ]; then
    echo "Активация виртуального окружения..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Активация виртуального окружения..."
    source .venv/bin/activate
fi

# Установка зависимостей если нужно
if ! python3 -m pytest --version &> /dev/null; then
    echo "Установка зависимостей для тестирования..."
    pip install -q pytest pytest-asyncio pytest-cov httpx
fi

echo ""
echo "1. Проверка синтаксиса тестов..."
python3 -m py_compile tests/*.py 2>&1 && echo "✓ Синтаксис тестов корректен"

echo ""
echo "2. Запуск unit тестов..."
python3 -m pytest tests/test_exceptions.py -v
python3 -m pytest tests/test_security.py -v
python3 -m pytest tests/test_retry.py -v
python3 -m pytest tests/test_graph_rag.py -v

echo ""
echo "3. Запуск integration тестов..."
python3 -m pytest tests/test_api_integration.py -v

echo ""
echo "4. Запуск всех тестов с покрытием..."
python3 -m pytest tests/ --cov=shared --cov=services --cov=api_gateway --cov-report=term-missing --cov-report=html

echo ""
echo "=========================================="
echo "Тестирование завершено!"
echo "Отчет о покрытии: htmlcov/index.html"
echo "=========================================="

