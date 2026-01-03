-- Миграция для создания схемы prompts в Supabase
-- Выполнить в SQL Editor Supabase

-- Создать схему prompts
CREATE SCHEMA IF NOT EXISTS prompts;

-- Создать таблицу для хранения промптов
CREATE TABLE IF NOT EXISTS prompts.prompts (
    id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    agent_type TEXT NOT NULL,
    prompt_type TEXT NOT NULL,
    template TEXT NOT NULL,
    variables JSONB DEFAULT '[]'::jsonb,
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, version)
);

-- Создать индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_prompts_agent_type ON prompts.prompts(agent_type);
CREATE INDEX IF NOT EXISTS idx_prompts_prompt_type ON prompts.prompts(prompt_type);
CREATE INDEX IF NOT EXISTS idx_prompts_agent_prompt_type ON prompts.prompts(agent_type, prompt_type);
CREATE INDEX IF NOT EXISTS idx_prompts_active ON prompts.prompts(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_prompts_version ON prompts.prompts(id, version DESC);

-- Создать функцию для получения последней версии промпта
CREATE OR REPLACE FUNCTION prompts.get_latest_prompt(prompt_id TEXT)
RETURNS TABLE (
    id TEXT,
    name TEXT,
    description TEXT,
    agent_type TEXT,
    prompt_type TEXT,
    template TEXT,
    variables JSONB,
    version INTEGER,
    is_active BOOLEAN,
    metadata JSONB,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, p.description, p.agent_type, p.prompt_type, 
           p.template, p.variables, p.version, p.is_active, p.metadata,
           p.created_at, p.updated_at
    FROM prompts.prompts p
    WHERE p.id = prompt_id
      AND p.is_active = true
    ORDER BY p.version DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Создать функцию для получения активных промптов агента
CREATE OR REPLACE FUNCTION prompts.get_agent_prompts(
    agent_type_param TEXT,
    prompt_type_param TEXT DEFAULT NULL
)
RETURNS TABLE (
    id TEXT,
    name TEXT,
    description TEXT,
    agent_type TEXT,
    prompt_type TEXT,
    template TEXT,
    variables JSONB,
    version INTEGER,
    is_active BOOLEAN,
    metadata JSONB,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (p.id)
           p.id, p.name, p.description, p.agent_type, p.prompt_type,
           p.template, p.variables, p.version, p.is_active, p.metadata,
           p.created_at, p.updated_at
    FROM prompts.prompts p
    WHERE p.agent_type = agent_type_param
      AND p.is_active = true
      AND (prompt_type_param IS NULL OR p.prompt_type = prompt_type_param)
    ORDER BY p.id, p.version DESC;
END;
$$ LANGUAGE plpgsql;

-- Включить Row Level Security
ALTER TABLE prompts.prompts ENABLE ROW LEVEL SECURITY;

-- Политика: все могут читать активные промпты
CREATE POLICY "Anyone can read active prompts"
ON prompts.prompts
FOR SELECT
USING (is_active = true);

-- Политика: только service role может изменять промпты
-- (в production настроить через Supabase Dashboard)

-- Создать триггер для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION prompts.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_prompts_updated_at
BEFORE UPDATE ON prompts.prompts
FOR EACH ROW
EXECUTE FUNCTION prompts.update_updated_at();

-- Комментарии к таблице и колонкам
COMMENT ON SCHEMA prompts IS 'Схема для хранения промптов ИИ агентов';
COMMENT ON TABLE prompts.prompts IS 'Таблица промптов с версионированием';
COMMENT ON COLUMN prompts.prompts.id IS 'Уникальный идентификатор промпта';
COMMENT ON COLUMN prompts.prompts.version IS 'Версия промпта (увеличивается при обновлении)';
COMMENT ON COLUMN prompts.prompts.is_active IS 'Активен ли промпт';
COMMENT ON COLUMN prompts.prompts.variables IS 'Список переменных в шаблоне (JSON массив)';
COMMENT ON COLUMN prompts.prompts.metadata IS 'Дополнительные метаданные (температура, настройки и т.д.)';

