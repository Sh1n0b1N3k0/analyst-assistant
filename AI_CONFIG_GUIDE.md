# Руководство по настройке ИИ моделей

## Обзор

Система поддерживает настройку ИИ моделей на двух уровнях:
1. **Глобальные настройки** - применяются ко всем агентам по умолчанию
2. **Агент-специфичные настройки** - переопределяют глобальные для конкретного агента

## Поддерживаемые провайдеры

- **OpenAI** - GPT-4, GPT-3.5 и другие модели OpenAI
- **Anthropic** - Claude 3 (Opus, Sonnet, Haiku)
- **Azure OpenAI** - OpenAI модели через Azure
- **OpenRouter** - Единый API для множества моделей
- **Ollama** - Локальные модели (не требует API ключ)

## Приоритет конфигурации

При настройке агента система использует следующий приоритет:

1. **Агент-специфичный API ключ** (если указан)
2. **Провайдер-специфичный API ключ** (например, `OPENAI_API_KEY`)
3. **Агент-специфичный провайдер** (если указан)
4. **Глобальный провайдер** (`AI_PROVIDER`)

## Примеры конфигурации

### Пример 1: Все агенты используют OpenAI

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

### Пример 2: Разные провайдеры для разных агентов

```env
# Базовый провайдер
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Администратор проекта использует Anthropic
AI_PROJECT_ADMIN_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Обработчик требований использует OpenAI
AI_REQUIREMENT_PROCESSOR_PROVIDER=openai
# Использует OPENAI_API_KEY из базовой конфигурации

# База знаний использует Azure OpenAI
AI_KNOWLEDGE_BASE_PROVIDER=azure_openai
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment
```

### Пример 3: Разные API ключи для одного провайдера

```env
# Базовый OpenAI ключ
AI_PROVIDER=openai
OPENAI_API_KEY=sk-base-key...

# Администратор проекта использует свой OpenAI ключ
AI_PROJECT_ADMIN_PROVIDER=openai
AI_PROJECT_ADMIN_API_KEY=sk-project-admin-key...

# Остальные агенты используют базовый ключ
```

### Пример 4: Разные модели для разных агентов

```env
# Базовые настройки
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
AI_OPENAI_MODEL=gpt-4-turbo-preview

# Администратор проекта использует GPT-4
AI_PROJECT_ADMIN_MODEL=gpt-4

# Обработчик требований использует GPT-3.5 (быстрее и дешевле)
AI_REQUIREMENT_PROCESSOR_MODEL=gpt-3.5-turbo

# База знаний использует Claude (лучше для анализа)
AI_KNOWLEDGE_BASE_PROVIDER=anthropic
AI_KNOWLEDGE_BASE_MODEL=claude-3-opus-20240229
ANTHROPIC_API_KEY=sk-ant-...
```

### Пример 5: Использование OpenRouter

```env
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...
AI_OPENROUTER_MODEL=openai/gpt-4-turbo

# Или для конкретного агента
AI_SPEC_GENERATOR_PROVIDER=openrouter
AI_SPEC_GENERATOR_MODEL=anthropic/claude-3-opus
AI_SPEC_GENERATOR_API_KEY=sk-or-...
```

### Пример 6: Локальная разработка с Ollama

```env
# Для локальной разработки без API ключей
AI_PROVIDER=ollama
AI_OLLAMA_BASE_URL=http://localhost:11434
AI_OLLAMA_MODEL=llama2

# Или смешанный подход
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Только для разработки - используем локальную модель
AI_REQUIREMENT_PROCESSOR_PROVIDER=ollama
AI_REQUIREMENT_PROCESSOR_MODEL=llama2
```

## Настройка температуры

Температура контролирует "креативность" модели:
- **0.0-0.3** - очень детерминированные ответы
- **0.7** - баланс (по умолчанию)
- **0.9-1.0** - более креативные ответы

```env
# Глобальная температура
AI_OPENAI_TEMPERATURE=0.7

# Для конкретного агента
AI_PROJECT_ADMIN_TEMPERATURE=0.5  # Более детерминированные рекомендации
AI_SPEC_GENERATOR_TEMPERATURE=0.9  # Более креативная генерация
```

## Azure OpenAI

Для использования Azure OpenAI нужны дополнительные параметры:

```env
AI_PROVIDER=azure_openai
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AI_AZURE_OPENAI_MODEL=gpt-4
```

## Проверка конфигурации

Для проверки конфигурации можно использовать:

```python
from shared.ai_config import ai_settings

# Проверить конфигурацию для агента
config = ai_settings.get_config_for_agent("project_admin")
print(config)
# {
#     "provider": "openai",
#     "model": "gpt-4-turbo-preview",
#     "temperature": 0.7,
#     "api_key": "sk-...",
#     ...
# }
```

## Рекомендации

1. **Для production**: Используйте разные API ключи для разных агентов для лучшего контроля расходов
2. **Для разработки**: Используйте Ollama или более дешевые модели (GPT-3.5)
3. **Для анализа**: Используйте Claude (лучше для анализа текста)
4. **Для генерации**: Используйте GPT-4 (лучше для генерации контента)
5. **Для экономии**: Используйте OpenRouter для доступа к разным моделям по единой цене

## Troubleshooting

### Проблема: "API key not found"
- Проверьте, что указан правильный API ключ для выбранного провайдера
- Убедитесь, что ключ не содержит лишних пробелов

### Проблема: "Model not found"
- Проверьте правильность названия модели
- Для Azure OpenAI убедитесь, что deployment name правильный

### Проблема: "Rate limit exceeded"
- Используйте разные API ключи для разных агентов
- Рассмотрите использование OpenRouter для лучшего rate limiting

### Проблема: Ollama не подключается
- Убедитесь, что Ollama запущен: `ollama serve`
- Проверьте `AI_OLLAMA_BASE_URL`

