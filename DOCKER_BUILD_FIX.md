# Решение проблем сборки Docker образа

## Проблема: Ошибка установки зависимостей

### Ошибка
```
target api_gateway: failed to solve: process "/bin/sh -c pip install --no-cache-dir -r requirements.txt" 
did not complete successfully: exit code: 1
```

## Решения

### 1. Обновлены версии пакетов

Обновлены версии langchain пакетов до совместимых:
- `langchain==0.1.20` (было 0.1.0)
- `langchain-openai==0.1.7` (было 0.0.5)
- `langchain-community==0.0.38` (было 0.0.20)
- `langchain-anthropic==0.1.23` (было 0.1.0)
- `langchain-core==0.1.52` (было 0.1.0)

### 2. Улучшен Dockerfile

- Добавлены системные зависимости: `g++`, `libpq-dev`
- Обновление pip перед установкой
- Установка базовых пакетов сначала

### 3. Создан requirements-docker.txt

Отдельный файл зависимостей для Docker без тестовых пакетов.

## Текущее решение

Dockerfile теперь устанавливает пакеты по частям для лучшей диагностики:
1. Базовые пакеты (FastAPI, Pydantic)
2. Database пакеты
3. Supabase пакеты
4. Langchain пакеты (с fallback на гибкие версии)
5. AI провайдеры
6. Утилиты

Это позволяет точно определить, какой пакет вызывает проблему.

### Если сборка все еще падает:

1. **Проверьте, на каком этапе падает сборка**:
```bash
docker-compose build --progress=plain api_gateway 2>&1 | grep -A 10 "RUN pip"
```
Это покажет, какой именно пакет вызывает проблему.

2. **Используйте упрощенный Dockerfile** (без langchain для диагностики):
```bash
docker build -f Dockerfile.api_gateway.simple -t api_gateway:simple .
```
Если упрощенная версия собирается, проблема в langchain пакетах.

3. **Проверьте конкретный проблемный пакет**:
```bash
docker run --rm -it python:3.11-slim bash
pip install --upgrade pip setuptools wheel
pip install <problematic-package>
```

4. **Попробуйте установить langchain без версий** (pip сам выберет совместимые):
В Dockerfile замените langchain секцию на:
```dockerfile
RUN pip install --no-cache-dir langchain langchain-core langchain-community langchain-openai langchain-anthropic
```

## Диагностика

Если проблема сохраняется, выполните:

```bash
# Сборка с подробным выводом
docker build --progress=plain --no-cache -t api_gateway -f Dockerfile.api_gateway .

# Просмотр логов сборки
docker-compose build api_gateway 2>&1 | tee build.log

# Проверка последних ошибок
tail -100 build.log | grep -i error
```

## Альтернативные решения

### Вариант 1: Использовать более новые версии

Обновите `requirements-docker.txt` с более новыми версиями:

```txt
langchain>=0.1.0,<0.2.0
langchain-openai>=0.1.0
langchain-community>=0.0.30
```

### Вариант 2: Установка без конкретных версий

Для langchain пакетов можно использовать диапазоны версий вместо точных:

```txt
langchain>=0.1.0,<0.2.0
langchain-openai>=0.1.0,<0.2.0
```

### Вариант 3: Многоэтапная сборка

Если проблема в конкретном пакете, можно установить проблемные пакеты отдельно:

```dockerfile
RUN pip install --no-cache-dir langchain-core langchain-community
RUN pip install --no-cache-dir -r requirements.txt
```

## Проверка совместимости

Проверьте совместимость версий на:
- [PyPI LangChain](https://pypi.org/project/langchain/)
- [LangChain GitHub Releases](https://github.com/langchain-ai/langchain/releases)

## Частые проблемы

### 1. Конфликт версий langchain

Решение: Используйте совместимые версии из одного релиза.

### 2. Проблемы с компиляцией (psycopg2, cryptography)

Решение: Убедитесь, что установлены `gcc`, `g++`, `libpq-dev`.

### 3. Недостаточно памяти

Решение: Увеличьте память Docker или используйте `--memory` флаг.

### 4. Проблемы с сетью

Решение: Проверьте доступ к PyPI, возможно нужен proxy.

## Команды для проверки

```bash
# Проверка синтаксиса Dockerfile
docker build --dry-run -f Dockerfile.api_gateway .

# Тестовая сборка без кэша
docker build --no-cache -t test-api-gateway -f Dockerfile.api_gateway .

# Проверка установленных пакетов
docker run --rm test-api-gateway pip list
```

