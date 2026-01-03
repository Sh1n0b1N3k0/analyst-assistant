-- ============================================================================
-- Скрипт инициализации базы данных для системы управления требованиями
-- Версия: 1.4.1
-- База данных: PostgreSQL
-- ============================================================================

-- Включение расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Для полнотекстового поиска

-- ============================================================================
-- Удаление существующих таблиц (если нужно пересоздать)
-- ============================================================================
-- Раскомментируйте для полной пересборки:
-- DROP TABLE IF EXISTS ui_entity_links CASCADE;
-- DROP TABLE IF EXISTS component_entities CASCADE;
-- DROP TABLE IF EXISTS requirement_entities CASCADE;
-- DROP TABLE IF EXISTS entity_relationships CASCADE;
-- DROP TABLE IF EXISTS entities CASCADE;
-- DROP TABLE IF EXISTS deployments CASCADE;
-- DROP TABLE IF EXISTS external_systems CASCADE;
-- DROP TABLE IF EXISTS metrics CASCADE;
-- DROP TABLE IF EXISTS risks CASCADE;
-- DROP TABLE IF EXISTS documents CASCADE;
-- DROP TABLE IF EXISTS test_cases CASCADE;
-- DROP TABLE IF EXISTS comments CASCADE;
-- DROP TABLE IF EXISTS change_history CASCADE;
-- DROP TABLE IF EXISTS message_broker_details CASCADE;
-- DROP TABLE IF EXISTS component_ui_links CASCADE;
-- DROP TABLE IF EXISTS component_requirement_links CASCADE;
-- DROP TABLE IF EXISTS component_dependencies CASCADE;
-- DROP TABLE IF EXISTS system_components CASCADE;
-- DROP TABLE IF EXISTS ui_elements CASCADE;
-- DROP TABLE IF EXISTS system_capabilities CASCADE;
-- DROP TABLE IF EXISTS requirement_relationships CASCADE;
-- DROP TABLE IF EXISTS requirements CASCADE;
-- DROP TABLE IF EXISTS projects CASCADE;
-- DROP TABLE IF EXISTS role_permissions CASCADE;
-- DROP TABLE IF EXISTS user_roles CASCADE;
-- DROP TABLE IF EXISTS permissions CASCADE;
-- DROP TABLE IF EXISTS roles CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;

-- ============================================================================
-- RBAC: Пользователи и права доступа
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_type TEXT NOT NULL,
    action TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(resource_type, action)
);

CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE role_permissions (
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- ============================================================================
-- Проекты
-- ============================================================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    methodology TEXT,  -- enum: agile, waterfall, hybrid, etc.
    start_date DATE,
    end_date DATE,
    status TEXT,  -- enum: planning, active, on_hold, completed, cancelled
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Требования
-- ============================================================================

CREATE TABLE requirements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    identifier TEXT NOT NULL,
    name TEXT NOT NULL,
    shall TEXT NOT NULL,
    rationale TEXT NOT NULL,
    verification_method TEXT NOT NULL,
    status TEXT,  -- enum: draft, in_review, approved, rejected, implemented, archived
    category TEXT,  -- enum: functional, non_functional, business, technical
    priority INTEGER CHECK (priority >= 1 AND priority <= 5),
    source TEXT,  -- stakeholder, regulation, etc.
    acceptance_criteria TEXT[],
    tags TEXT[],
    estimated_effort NUMERIC,
    actual_effort NUMERIC,
    due_date DATE,
    assigned_to_id UUID REFERENCES users(id) ON DELETE SET NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE(project_id, identifier)
);

-- ============================================================================
-- Связи между требованиями
-- ============================================================================

CREATE TABLE requirement_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_requirement_id UUID NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    to_requirement_id UUID NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL,  -- enum: depends_on, conflicts_with, duplicates, refines, replaces, related_to
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    CHECK (from_requirement_id != to_requirement_id)
);

-- ============================================================================
-- Функции системы
-- ============================================================================

CREATE TABLE system_capabilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    business_value TEXT,
    status TEXT,  -- enum: planned, in_development, completed, deprecated
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by_id UUID REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================================
-- Пользовательские интерфейсы
-- ============================================================================

CREATE TABLE ui_elements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT,  -- enum: screen, form, field, button, etc.
    description TEXT,
    capability_id UUID REFERENCES system_capabilities(id) ON DELETE SET NULL,
    parent_id UUID REFERENCES ui_elements(id) ON DELETE CASCADE,
    prototype_url TEXT,
    wireframe_url TEXT,
    accessibility_level TEXT,  -- enum: A, AA, AAA (WCAG levels)
    responsive_breakpoints JSONB,
    user_roles TEXT[],
    status TEXT,  -- enum: draft, in_design, approved, implemented
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by_id UUID REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================================
-- Системные компоненты
-- ============================================================================

CREATE TABLE system_components (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- enum: microservice, library, database, api_gateway, frontend_app, batch_job, event_handler, external_system, message_broker
    description TEXT,
    tech_stack TEXT[],
    parent_component_id UUID REFERENCES system_components(id) ON DELETE SET NULL,
    system_capability_id UUID REFERENCES system_capabilities(id) ON DELETE SET NULL,
    status TEXT,  -- enum: planned, in_development, deployed, deprecated
    health_status TEXT,  -- enum: healthy, degraded, down
    last_health_check TIMESTAMPTZ,
    monitoring_url TEXT,
    metrics_endpoint TEXT,
    logs_url TEXT,
    deployment_config JSONB,
    environment_variables JSONB,
    resource_limits JSONB,
    version TEXT,
    docs_url TEXT,
    source_code_url TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by_id UUID REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================================
-- Зависимости компонентов
-- ============================================================================

CREATE TABLE component_dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_component_id UUID NOT NULL REFERENCES system_components(id) ON DELETE CASCADE,
    to_component_id UUID NOT NULL REFERENCES system_components(id) ON DELETE CASCADE,
    type TEXT NOT NULL,  -- enum: calls, publishes, subscribes, reads, writes, uses, deployed_with
    protocol TEXT,
    interface TEXT,
    is_critical BOOLEAN DEFAULT FALSE,
    timeout INTEGER,
    retry_policy JSONB,
    circuit_breaker BOOLEAN DEFAULT FALSE,
    monitoring_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CHECK (from_component_id != to_component_id)
);

-- ============================================================================
-- Трассировка компонент ↔ требования
-- ============================================================================

CREATE TABLE component_requirement_links (
    component_id UUID NOT NULL REFERENCES system_components(id) ON DELETE CASCADE,
    requirement_id UUID NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    implementation_detail TEXT,
    coverage_level TEXT,  -- full, partial, planned
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    PRIMARY KEY (component_id, requirement_id)
);

-- ============================================================================
-- Трассировка компонент ↔ UI
-- ============================================================================

CREATE TABLE component_ui_links (
    component_id UUID NOT NULL REFERENCES system_components(id) ON DELETE CASCADE,
    ui_element_id UUID NOT NULL REFERENCES ui_elements(id) ON DELETE CASCADE,
    interaction TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (component_id, ui_element_id)
);

-- ============================================================================
-- Детали брокера сообщений
-- ============================================================================

CREATE TABLE message_broker_details (
    component_id UUID PRIMARY KEY REFERENCES system_components(id) ON DELETE CASCADE,
    broker_type TEXT NOT NULL,  -- enum: kafka, rabbitmq, nats, redis, etc.
    cluster_name TEXT,
    namespace TEXT,
    topics JSONB,
    queues JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- История изменений и аудит
-- ============================================================================

CREATE TABLE change_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT NOT NULL,  -- requirement, component, ui_element, etc.
    entity_id UUID NOT NULL,
    action TEXT NOT NULL,  -- enum: created, updated, deleted, status_changed
    old_values JSONB,
    new_values JSONB,
    changed_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    comment TEXT
);

-- ============================================================================
-- Комментарии и обсуждения
-- ============================================================================

CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT NOT NULL,  -- requirement, component, ui_element
    entity_id UUID NOT NULL,
    parent_comment_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    is_resolved BOOLEAN DEFAULT FALSE
);

-- ============================================================================
-- Тест-кейсы и верификация
-- ============================================================================

CREATE TABLE test_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requirement_id UUID REFERENCES requirements(id) ON DELETE CASCADE,
    component_id UUID REFERENCES system_components(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    test_type TEXT NOT NULL,  -- enum: unit, integration, e2e, performance, security
    status TEXT,  -- enum: not_run, passed, failed, blocked
    execution_date TIMESTAMPTZ,
    executed_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    test_result JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CHECK (requirement_id IS NOT NULL OR component_id IS NOT NULL)
);

-- ============================================================================
-- Документация и артефакты
-- ============================================================================

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    entity_type TEXT,  -- requirement, component, ui_element
    entity_id UUID,
    name TEXT NOT NULL,
    document_type TEXT NOT NULL,  -- enum: spec, diagram, api_doc, user_guide
    file_path TEXT,
    file_url TEXT,
    content TEXT,
    version INTEGER DEFAULT 1,
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Риски и проблемы
-- ============================================================================

CREATE TABLE risks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    requirement_id UUID REFERENCES requirements(id) ON DELETE SET NULL,
    component_id UUID REFERENCES system_components(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    risk_level TEXT NOT NULL,  -- enum: low, medium, high, critical
    probability INTEGER CHECK (probability >= 1 AND probability <= 5),
    impact INTEGER CHECK (impact >= 1 AND impact <= 5),
    mitigation_strategy TEXT,
    status TEXT,  -- enum: open, mitigated, accepted, closed
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Метрики и KPI
-- ============================================================================

CREATE TABLE metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    metric_type TEXT NOT NULL,  -- enum: requirement_coverage, test_coverage, component_health
    entity_type TEXT,
    entity_id UUID,
    value NUMERIC,
    target_value NUMERIC,
    unit TEXT,
    measured_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Внешние системы и интеграции
-- ============================================================================

CREATE TABLE external_systems (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_id UUID NOT NULL REFERENCES system_components(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    system_type TEXT,  -- API, database, service
    endpoint_url TEXT,
    authentication_type TEXT,
    api_version TEXT,
    documentation_url TEXT,
    status TEXT,  -- enum: active, deprecated, unavailable
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Развертывание и окружения
-- ============================================================================

CREATE TABLE deployments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_id UUID NOT NULL REFERENCES system_components(id) ON DELETE CASCADE,
    environment TEXT NOT NULL,  -- enum: development, staging, production
    version TEXT,
    deployed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deployed_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status TEXT,  -- enum: success, failed, rolling_back
    deployment_url TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Сущности системы
-- ============================================================================

CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,  -- enum: actor, data_object, business_process, external_system, resource
    description TEXT,
    attributes JSONB,
    status TEXT,  -- enum: active, deprecated, archived
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by_id UUID REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================================
-- Связи между сущностями
-- ============================================================================

CREATE TABLE entity_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    to_entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL,  -- enum: uses, creates, reads, updates, deletes, triggers, belongs_to, contains
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    CHECK (from_entity_id != to_entity_id)
);

-- ============================================================================
-- Связь требований с сущностями
-- ============================================================================

CREATE TABLE requirement_entities (
    requirement_id UUID NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    involvement_type TEXT NOT NULL,  -- enum: primary, secondary, affected, stakeholder
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    PRIMARY KEY (requirement_id, entity_id)
);

-- ============================================================================
-- Связь компонентов с сущностями
-- ============================================================================

CREATE TABLE component_entities (
    component_id UUID NOT NULL REFERENCES system_components(id) ON DELETE CASCADE,
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    interaction_type TEXT NOT NULL,  -- enum: manages, processes, stores, exposes, consumes
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    PRIMARY KEY (component_id, entity_id)
);

-- ============================================================================
-- Связь UI элементов с сущностями
-- ============================================================================

CREATE TABLE ui_entity_links (
    ui_element_id UUID NOT NULL REFERENCES ui_elements(id) ON DELETE CASCADE,
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    display_type TEXT NOT NULL,  -- enum: displays, edits, creates, deletes, filters
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    PRIMARY KEY (ui_element_id, entity_id)
);

-- ============================================================================
-- Индексы для оптимизации запросов
-- ============================================================================

-- Пользователи
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Проекты
CREATE INDEX idx_projects_owner_id ON projects(owner_id);
CREATE INDEX idx_projects_status ON projects(status);

-- Требования
CREATE INDEX idx_requirements_project_id ON requirements(project_id);
CREATE INDEX idx_requirements_identifier ON requirements(project_id, identifier);
CREATE INDEX idx_requirements_status ON requirements(status);
CREATE INDEX idx_requirements_category ON requirements(category);
CREATE INDEX idx_requirements_priority ON requirements(priority);
CREATE INDEX idx_requirements_assigned_to_id ON requirements(assigned_to_id);
CREATE INDEX idx_requirements_created_by_id ON requirements(created_by_id);
CREATE INDEX idx_requirements_tags ON requirements USING GIN(tags);
CREATE INDEX idx_requirements_fulltext ON requirements USING GIN(to_tsvector('russian', name || ' ' || COALESCE(shall, '')));

-- Связи требований
CREATE INDEX idx_requirement_relationships_from ON requirement_relationships(from_requirement_id);
CREATE INDEX idx_requirement_relationships_to ON requirement_relationships(to_requirement_id);
CREATE INDEX idx_requirement_relationships_type ON requirement_relationships(relationship_type);

-- Функции системы
CREATE INDEX idx_system_capabilities_project_id ON system_capabilities(project_id);
CREATE INDEX idx_system_capabilities_status ON system_capabilities(status);

-- UI элементы
CREATE INDEX idx_ui_elements_project_id ON ui_elements(project_id);
CREATE INDEX idx_ui_elements_capability_id ON ui_elements(capability_id);
CREATE INDEX idx_ui_elements_parent_id ON ui_elements(parent_id);

-- Компоненты
CREATE INDEX idx_system_components_project_id ON system_components(project_id);
CREATE INDEX idx_system_components_type ON system_components(type);
CREATE INDEX idx_system_components_status ON system_components(status);
CREATE INDEX idx_system_components_health_status ON system_components(health_status);
CREATE INDEX idx_system_components_parent_id ON system_components(parent_component_id);
CREATE INDEX idx_system_components_capability_id ON system_components(system_capability_id);

-- Зависимости компонентов
CREATE INDEX idx_component_dependencies_from ON component_dependencies(from_component_id);
CREATE INDEX idx_component_dependencies_to ON component_dependencies(to_component_id);
CREATE INDEX idx_component_dependencies_type ON component_dependencies(type);
CREATE INDEX idx_component_dependencies_critical ON component_dependencies(is_critical) WHERE is_critical = TRUE;

-- История изменений
CREATE INDEX idx_change_history_entity ON change_history(entity_type, entity_id);
CREATE INDEX idx_change_history_changed_by ON change_history(changed_by_id);
CREATE INDEX idx_change_history_changed_at ON change_history(changed_at DESC);
CREATE INDEX idx_change_history_action ON change_history(action);

-- Комментарии
CREATE INDEX idx_comments_entity ON comments(entity_type, entity_id);
CREATE INDEX idx_comments_parent ON comments(parent_comment_id);
CREATE INDEX idx_comments_created_by ON comments(created_by_id);
CREATE INDEX idx_comments_resolved ON comments(is_resolved) WHERE is_resolved = FALSE;

-- Тест-кейсы
CREATE INDEX idx_test_cases_requirement_id ON test_cases(requirement_id);
CREATE INDEX idx_test_cases_component_id ON test_cases(component_id);
CREATE INDEX idx_test_cases_status ON test_cases(status);
CREATE INDEX idx_test_cases_test_type ON test_cases(test_type);

-- Документация
CREATE INDEX idx_documents_project_id ON documents(project_id);
CREATE INDEX idx_documents_entity ON documents(entity_type, entity_id);
CREATE INDEX idx_documents_type ON documents(document_type);

-- Риски
CREATE INDEX idx_risks_project_id ON risks(project_id);
CREATE INDEX idx_risks_requirement_id ON risks(requirement_id);
CREATE INDEX idx_risks_component_id ON risks(component_id);
CREATE INDEX idx_risks_risk_level ON risks(risk_level);
CREATE INDEX idx_risks_status ON risks(status);

-- Метрики
CREATE INDEX idx_metrics_project_id ON metrics(project_id);
CREATE INDEX idx_metrics_entity ON metrics(entity_type, entity_id);
CREATE INDEX idx_metrics_type ON metrics(metric_type);
CREATE INDEX idx_metrics_measured_at ON metrics(measured_at DESC);

-- Сущности
CREATE INDEX idx_entities_project_id ON entities(project_id);
CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_entities_name ON entities(name);
CREATE INDEX idx_entities_attributes ON entities USING GIN(attributes);

-- Связи сущностей
CREATE INDEX idx_entity_relationships_from ON entity_relationships(from_entity_id);
CREATE INDEX idx_entity_relationships_to ON entity_relationships(to_entity_id);
CREATE INDEX idx_entity_relationships_type ON entity_relationships(relationship_type);

-- ============================================================================
-- Триггеры для автоматического обновления updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_requirements_updated_at BEFORE UPDATE ON requirements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_capabilities_updated_at BEFORE UPDATE ON system_capabilities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ui_elements_updated_at BEFORE UPDATE ON ui_elements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_components_updated_at BEFORE UPDATE ON system_components
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_message_broker_details_updated_at BEFORE UPDATE ON message_broker_details
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_test_cases_updated_at BEFORE UPDATE ON test_cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_risks_updated_at BEFORE UPDATE ON risks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_external_systems_updated_at BEFORE UPDATE ON external_systems
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Инициализация базовых данных
-- ============================================================================

-- Создание ролей по умолчанию
INSERT INTO roles (name, description) VALUES
    ('admin', 'Администратор с полным доступом ко всем ресурсам'),
    ('analyst', 'Бизнес-аналитик - может создавать и управлять требованиями и артефактами'),
    ('reviewer', 'Ревьюер - может проверять, одобрять и отклонять требования'),
    ('developer', 'Разработчик - может читать требования и артефакты'),
    ('viewer', 'Просмотр - только чтение требований')
ON CONFLICT (name) DO NOTHING;

-- Создание прав доступа по умолчанию
INSERT INTO permissions (resource_type, action, description) VALUES
    -- Требования
    ('requirement', 'create', 'Создание требований'),
    ('requirement', 'read', 'Чтение требований'),
    ('requirement', 'update', 'Обновление требований'),
    ('requirement', 'delete', 'Удаление требований'),
    ('requirement', 'approve', 'Одобрение требований'),
    ('requirement', 'reject', 'Отклонение требований'),
    -- Компоненты
    ('component', 'create', 'Создание компонентов'),
    ('component', 'read', 'Чтение компонентов'),
    ('component', 'update', 'Обновление компонентов'),
    ('component', 'delete', 'Удаление компонентов'),
    -- UI элементы
    ('ui_element', 'create', 'Создание UI элементов'),
    ('ui_element', 'read', 'Чтение UI элементов'),
    ('ui_element', 'update', 'Обновление UI элементов'),
    ('ui_element', 'delete', 'Удаление UI элементов'),
    -- Пользователи
    ('user', 'create', 'Создание пользователей'),
    ('user', 'read', 'Чтение пользователей'),
    ('user', 'update', 'Обновление пользователей'),
    ('user', 'delete', 'Удаление пользователей'),
    -- Роли
    ('role', 'create', 'Создание ролей'),
    ('role', 'read', 'Чтение ролей'),
    ('role', 'update', 'Обновление ролей'),
    ('role', 'delete', 'Удаление ролей')
ON CONFLICT (resource_type, action) DO NOTHING;

-- Назначение прав ролям
-- Администратор получает все права
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'admin'
ON CONFLICT DO NOTHING;

-- Аналитик получает права на требования, компоненты и UI
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'analyst'
    AND p.resource_type IN ('requirement', 'component', 'ui_element')
    AND p.action IN ('create', 'read', 'update')
ON CONFLICT DO NOTHING;

-- Ревьюер получает права на чтение и одобрение/отклонение
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'reviewer'
    AND p.resource_type IN ('requirement', 'component', 'ui_element')
    AND p.action IN ('read', 'approve', 'reject')
ON CONFLICT DO NOTHING;

-- Разработчик получает права на чтение
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'developer'
    AND p.resource_type IN ('requirement', 'component', 'ui_element')
    AND p.action = 'read'
ON CONFLICT DO NOTHING;

-- Просмотр получает права на чтение
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'viewer'
    AND p.resource_type IN ('requirement', 'component', 'ui_element')
    AND p.action = 'read'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Представления для удобных запросов
-- ============================================================================

-- Представление для требований с информацией о создателе и исполнителе
CREATE OR REPLACE VIEW requirements_view AS
SELECT 
    r.*,
    creator.username AS created_by_username,
    creator.full_name AS created_by_full_name,
    updater.username AS updated_by_username,
    updater.full_name AS updated_by_full_name,
    assignee.username AS assigned_to_username,
    assignee.full_name AS assigned_to_full_name,
    p.name AS project_name
FROM requirements r
LEFT JOIN users creator ON r.created_by_id = creator.id
LEFT JOIN users updater ON r.updated_by_id = updater.id
LEFT JOIN users assignee ON r.assigned_to_id = assignee.id
LEFT JOIN projects p ON r.project_id = p.id;

-- Представление для компонентов с информацией о здоровье
CREATE OR REPLACE VIEW components_health_view AS
SELECT 
    c.*,
    p.name AS project_name,
    cap.name AS capability_name,
    creator.username AS created_by_username,
    CASE 
        WHEN c.health_status = 'down' THEN 'Критично'
        WHEN c.health_status = 'degraded' THEN 'Предупреждение'
        ELSE 'Норма'
    END AS health_status_label
FROM system_components c
LEFT JOIN projects p ON c.project_id = p.id
LEFT JOIN system_capabilities cap ON c.system_capability_id = cap.id
LEFT JOIN users creator ON c.created_by_id = creator.id;

-- Представление для трассировки требований
CREATE OR REPLACE VIEW requirement_traceability_view AS
SELECT 
    r.id AS requirement_id,
    r.identifier AS requirement_identifier,
    r.name AS requirement_name,
    c.id AS component_id,
    c.name AS component_name,
    crl.coverage_level,
    crl.implementation_detail
FROM requirements r
LEFT JOIN component_requirement_links crl ON r.id = crl.requirement_id
LEFT JOIN system_components c ON crl.component_id = c.id;

-- ============================================================================
-- Комментарии к таблицам
-- ============================================================================

COMMENT ON TABLE users IS 'Пользователи системы - аутентификация и авторизация';
COMMENT ON TABLE roles IS 'Роли пользователей - группировка прав доступа';
COMMENT ON TABLE permissions IS 'Права доступа - ресурсы и действия';
COMMENT ON TABLE projects IS 'Проекты - контекст для всех артефактов';
COMMENT ON TABLE requirements IS 'Требования - атомарные формулировки по ISO/IEC/IEEE 29148';
COMMENT ON TABLE requirement_relationships IS 'Связи между требованиями - зависимости, конфликты, дубликаты';
COMMENT ON TABLE system_capabilities IS 'Функции системы - логические возможности, группирующие требования';
COMMENT ON TABLE ui_elements IS 'Элементы интерфейса - экраны, формы, поля с иерархией';
COMMENT ON TABLE system_components IS 'Системные компоненты - реализации функций: сервисы, модули, БД';
COMMENT ON TABLE component_dependencies IS 'Зависимости компонентов - взаимодействия: вызовы, события, данные';
COMMENT ON TABLE component_requirement_links IS 'Реализация требований - как компонент удовлетворяет требованию';
COMMENT ON TABLE component_ui_links IS 'Взаимодействие UI-компонент - как интерфейс общается с бэкенд';
COMMENT ON TABLE message_broker_details IS 'Параметры брокера - топики, очереди, настройки кластера';
COMMENT ON TABLE change_history IS 'История изменений - полный аудит всех изменений артефактов';
COMMENT ON TABLE comments IS 'Комментарии - обсуждения и комментарии к артефактам';
COMMENT ON TABLE test_cases IS 'Тест-кейсы - верификация требований и компонентов';
COMMENT ON TABLE documents IS 'Документация - спецификации, диаграммы, API документация';
COMMENT ON TABLE risks IS 'Риски и проблемы - трекинг рисков и проблем проекта';
COMMENT ON TABLE metrics IS 'Метрики и KPI - отслеживание метрик выполнения требований';
COMMENT ON TABLE external_systems IS 'Внешние системы - детали внешних систем и интеграций';
COMMENT ON TABLE deployments IS 'Развертывание - информация о развертывании компонентов';
COMMENT ON TABLE entities IS 'Сущности системы - акторы, объекты данных, бизнес-процессы';
COMMENT ON TABLE entity_relationships IS 'Связи между сущностями - взаимодействия между сущностями';
COMMENT ON TABLE requirement_entities IS 'Связь требований с сущностями - какие сущности участвуют';
COMMENT ON TABLE component_entities IS 'Связь компонентов с сущностями - как компонент взаимодействует';
COMMENT ON TABLE ui_entity_links IS 'Связь UI элементов с сущностями - как UI работает с сущностью';

-- ============================================================================
-- Завершение
-- ============================================================================

-- Вывод информации о созданных таблицах
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE';
    
    RAISE NOTICE 'База данных инициализирована успешно!';
    RAISE NOTICE 'Создано таблиц: %', table_count;
    RAISE NOTICE 'Версия схемы: 1.4.1';
END $$;

