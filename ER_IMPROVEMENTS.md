# Предложения по улучшению ER-диаграммы

## Анализ текущей модели и рекомендации

### ✅ Сильные стороны текущей модели:
- Четкая структура требований по ISO/IEC/IEEE 29148
- Хорошая трассировка требований к компонентам
- Поддержка иерархий компонентов и UI
- Детальная модель зависимостей
- Поддержка брокеров сообщений

---

## 🔴 Критические дополнения

### 1. **Пользователи и права доступа (RBAC)**
**Проблема:** Нет модели пользователей, ролей и прав доступа

**Предложение:**
```plantuml
entity "users" as users {
  * id : UUID <<PK>>
  username : TEXT <<unique>>
  email : TEXT <<unique>>
  full_name : TEXT
  hashed_password : TEXT
  is_active : BOOLEAN
  created_at : TIMESTAMPTZ
}

entity "roles" as roles {
  * id : UUID <<PK>>
  name : TEXT <<unique>>
  description : TEXT
}

entity "permissions" as perms {
  * id : UUID <<PK>>
  resource_type : TEXT
  action : TEXT
  description : TEXT
}

entity "user_roles" as ur {
  * user_id : UUID <<FK PK>>
  * role_id : UUID <<FK PK>>
}

entity "role_permissions" as rp {
  * role_id : UUID <<FK PK>>
  * permission_id : UUID <<FK PK>>
}

users ||--o{ ur
roles ||--o{ ur
roles ||--o{ rp
perms ||--o{ rp
```

**Поля для добавления:**
- `created_by_id` в requirements, components, ui_elements
- `updated_by_id` в основных сущностях
- `assigned_to_id` в requirements (назначенный исполнитель)

---

### 2. **История изменений и аудит**
**Проблема:** Есть version, но нет детальной истории изменений

**Предложение:**
```plantuml
entity "change_history" as ch {
  * id : UUID <<PK>>
  entity_type : TEXT
  entity_id : UUID
  action : TEXT <<enum>>  -- created, updated, deleted, status_changed
  old_values : JSONB
  new_values : JSONB
  changed_by_id : UUID <<FK>>
  changed_at : TIMESTAMPTZ
  comment : TEXT
}

ch }o--|| users : "changed_by_id"
```

**Поля для добавления:**
- `created_at`, `updated_at`, `deleted_at` во все основные сущности
- `created_by_id`, `updated_by_id` во все основные сущности

---

### 3. **Связи между требованиями**
**Проблема:** Нет явных связей между требованиями (зависимости, конфликты, дубликаты)

**Предложение:**
```plantuml
entity "requirement_relationships" as req_rel {
  * id : UUID <<PK>>
  from_requirement_id : UUID <<FK>>
  to_requirement_id : UUID <<FK>>
  relationship_type : TEXT <<enum>>  -- depends_on, conflicts_with, duplicates, refines, replaces
  description : TEXT
  created_at : TIMESTAMPTZ
}

req_rel }o--|| req : "from_requirement_id"
req_rel }o--|| req : "to_requirement_id"
```

**Типы связей:**
- `depends_on` - зависит от
- `conflicts_with` - конфликтует с
- `duplicates` - дублирует
- `refines` - уточняет
- `replaces` - заменяет
- `related_to` - связано с

---

### 4. **Комментарии и обсуждения**
**Проблема:** Нет возможности комментировать требования и компоненты

**Предложение:**
```plantuml
entity "comments" as comments {
  * id : UUID <<PK>>
  entity_type : TEXT  -- requirement, component, ui_element
  entity_id : UUID
  parent_comment_id : UUID <<FK>>  -- для вложенных комментариев
  content : TEXT <<not null>>
  created_by_id : UUID <<FK>>
  created_at : TIMESTAMPTZ
  updated_at : TIMESTAMPTZ
  is_resolved : BOOLEAN
}

comments }o--o| comments : "parent_comment_id"
comments }o--|| users : "created_by_id"
```

---

### 5. **Тест-кейсы и верификация**
**Проблема:** Есть verification_method, но нет связи с конкретными тестами

**Предложение:**
```plantuml
entity "test_cases" as tests {
  * id : UUID <<PK>>
  requirement_id : UUID <<FK>>
  component_id : UUID <<FK>>
  name : TEXT <<not null>>
  description : TEXT
  test_type : TEXT <<enum>>  -- unit, integration, e2e, performance, security
  status : TEXT <<enum>>  -- not_run, passed, failed, blocked
  execution_date : TIMESTAMPTZ
  executed_by_id : UUID <<FK>>
  test_result : JSONB
}

tests }o--|| req : "requirement_id"
tests }o--|| comp : "component_id"
tests }o--|| users : "executed_by_id"
```

---

## 🟡 Важные дополнения

### 6. **Документация и артефакты**
**Проблема:** Нет модели для хранения документов и артефактов

**Предложение:**
```plantuml
entity "documents" as docs {
  * id : UUID <<PK>>
  project_id : UUID <<FK>>
  entity_type : TEXT
  entity_id : UUID
  name : TEXT <<not null>>
  document_type : TEXT <<enum>>  -- spec, diagram, api_doc, user_guide
  file_path : TEXT
  file_url : TEXT
  content : TEXT
  version : INT
  created_by_id : UUID <<FK>>
  created_at : TIMESTAMPTZ
}

docs }o--|| proj : "project_id"
docs }o--|| users : "created_by_id"
```

---

### 7. **Риски и проблемы**
**Проблема:** Нет трекинга рисков и проблем

**Предложение:**
```plantuml
entity "risks" as risks {
  * id : UUID <<PK>>
  project_id : UUID <<FK>>
  requirement_id : UUID <<FK>>
  component_id : UUID <<FK>>
  title : TEXT <<not null>>
  description : TEXT
  risk_level : TEXT <<enum>>  -- low, medium, high, critical
  probability : INT  -- 1-5
  impact : INT  -- 1-5
  mitigation_strategy : TEXT
  status : TEXT <<enum>>  -- open, mitigated, accepted, closed
  created_by_id : UUID <<FK>>
  created_at : TIMESTAMPTZ
}

risks }o--|| proj : "project_id"
risks }o--o| req : "requirement_id"
risks }o--o| comp : "component_id"
```

---

### 8. **Метрики и KPI**
**Проблема:** Нет отслеживания метрик выполнения требований

**Предложение:**
```plantuml
entity "metrics" as metrics {
  * id : UUID <<PK>>
  project_id : UUID <<FK>>
  metric_type : TEXT <<enum>>  -- requirement_coverage, test_coverage, component_health
  entity_type : TEXT
  entity_id : UUID
  value : NUMERIC
  target_value : NUMERIC
  unit : TEXT
  measured_at : TIMESTAMPTZ
}

metrics }o--|| proj : "project_id"
```

---

### 9. **Внешние системы и интеграции**
**Проблема:** Нет деталей внешних систем и интеграций

**Предложение:**
```plantuml
entity "external_systems" as ext_sys {
  * id : UUID <<PK>>
  component_id : UUID <<FK>>
  name : TEXT <<not null>>
  system_type : TEXT  -- API, database, service
  endpoint_url : TEXT
  authentication_type : TEXT
  api_version : TEXT
  documentation_url : TEXT
  status : TEXT <<enum>>  -- active, deprecated, unavailable
}

ext_sys }o--|| comp : "component_id"
```

---

### 10. **Развертывание и окружения**
**Проблема:** Нет информации о развертывании компонентов

**Предложение:**
```plantuml
entity "deployments" as depl {
  * id : UUID <<PK>>
  component_id : UUID <<FK>>
  environment : TEXT <<enum>>  -- development, staging, production
  version : TEXT
  deployed_at : TIMESTAMPTZ
  deployed_by_id : UUID <<FK>>
  status : TEXT <<enum>>  -- success, failed, rolling_back
  deployment_url : TEXT
}

depl }o--|| comp : "component_id"
depl }o--|| users : "deployed_by_id"
```

---

## 🟢 Улучшения существующих сущностей

### 11. **Улучшение requirements**
**Добавить поля:**
- `priority` (INT, 1-5) - приоритет требования
- `category` (TEXT, enum) - категория: functional, non-functional, business, technical
- `source` (TEXT) - источник требования (stakeholder, regulation, etc.)
- `acceptance_criteria` (TEXT[]) - критерии приемки (массив)
- `tags` (TEXT[]) - теги для поиска и фильтрации
- `estimated_effort` (NUMERIC) - оценка трудозатрат
- `actual_effort` (NUMERIC) - фактические трудозатраты
- `due_date` (DATE) - срок выполнения

---

### 12. **Улучшение system_components**
**Добавить поля:**
- `health_status` (TEXT, enum) - статус здоровья: healthy, degraded, down
- `last_health_check` (TIMESTAMPTZ) - последняя проверка
- `monitoring_url` (TEXT) - ссылка на мониторинг
- `metrics_endpoint` (TEXT) - endpoint для метрик
- `logs_url` (TEXT) - ссылка на логи
- `deployment_config` (JSONB) - конфигурация развертывания
- `environment_variables` (JSONB) - переменные окружения
- `resource_limits` (JSONB) - лимиты ресурсов (CPU, memory)

---

### 13. **Улучшение component_dependencies**
**Добавить поля:**
- `is_critical` (BOOLEAN) - критичность зависимости
- `timeout` (INT) - таймаут взаимодействия
- `retry_policy` (JSONB) - политика повторов
- `circuit_breaker` (BOOLEAN) - использование circuit breaker
- `monitoring_enabled` (BOOLEAN) - включен ли мониторинг

---

### 14. **Улучшение ui_elements**
**Добавить поля:**
- `prototype_url` (TEXT) - ссылка на прототип (Figma, etc.)
- `wireframe_url` (TEXT) - ссылка на wireframe
- `accessibility_level` (TEXT, enum) - уровень доступности (WCAG)
- `responsive_breakpoints` (JSONB) - точки останова для адаптивности
- `user_roles` (TEXT[]) - роли пользователей, имеющие доступ

---

### 15. **Улучшение projects**
**Добавить поля:**
- `description` (TEXT) - описание проекта
- `start_date` (DATE) - дата начала
- `end_date` (DATE) - дата окончания
- `status` (TEXT, enum) - статус проекта
- `owner_id` (UUID, FK) - владелец проекта
- `team_members` (UUID[]) - участники команды
- `budget` (NUMERIC) - бюджет проекта
- `repository_url` (TEXT) - ссылка на репозиторий

---

## 📊 Дополнительные сущности

### 16. **Спринты и итерации**
```plantuml
entity "sprints" as sprints {
  * id : UUID <<PK>>
  project_id : UUID <<FK>>
  name : TEXT <<not null>>
  start_date : DATE
  end_date : DATE
  goal : TEXT
  status : TEXT <<enum>>
}

entity "sprint_requirements" as spr_req {
  * sprint_id : UUID <<FK PK>>
  * requirement_id : UUID <<FK PK>>
  story_points : INT
}
```

---

### 17. **Уведомления и события**
```plantuml
entity "notifications" as notif {
  * id : UUID <<PK>>
  user_id : UUID <<FK>>
  entity_type : TEXT
  entity_id : UUID
  notification_type : TEXT <<enum>>
  message : TEXT
  is_read : BOOLEAN
  created_at : TIMESTAMPTZ
}
```

---

### 18. **Шаблоны и стандарты**
```plantuml
entity "templates" as templates {
  * id : UUID <<PK>>
  template_type : TEXT <<enum>>  -- requirement, component, ui_element
  name : TEXT <<not null>>
  content : JSONB
  is_default : BOOLEAN
}
```

---

### 19. **Экспорт и импорт**
```plantuml
entity "exports" as exports {
  * id : UUID <<PK>>
  project_id : UUID <<FK>>
  export_type : TEXT <<enum>>  -- requirements, architecture, full
  format : TEXT <<enum>>  -- json, xml, excel, docx
  file_path : TEXT
  exported_by_id : UUID <<FK>>
  exported_at : TIMESTAMPTZ
}
```

---

### 20. **Интеграции с внешними системами**
```plantuml
entity "integrations" as integrations {
  * id : UUID <<PK>>
  project_id : UUID <<FK>>
  integration_type : TEXT <<enum>>  -- jira, confluence, gitlab, github
  external_system_id : TEXT
  api_token : TEXT  -- encrypted
  sync_enabled : BOOLEAN
  last_sync_at : TIMESTAMPTZ
}
```

---

## 🎯 Приоритеты внедрения

### Высокий приоритет (критично):
1. ✅ Пользователи и права доступа (RBAC)
2. ✅ История изменений и аудит
3. ✅ Связи между требованиями
4. ✅ Комментарии и обсуждения
5. ✅ Тест-кейсы и верификация

### Средний приоритет (важно):
6. ✅ Документация и артефакты
7. ✅ Риски и проблемы
8. ✅ Метрики и KPI
9. ✅ Улучшение существующих сущностей (поля)

### Низкий приоритет (желательно):
10. ✅ Внешние системы и интеграции
11. ✅ Развертывание и окружения
12. ✅ Спринты и итерации
13. ✅ Уведомления и события
14. ✅ Шаблоны и стандарты

---

## 📝 Рекомендации по реализации

### Поэтапное внедрение:
1. **Фаза 1:** RBAC + История изменений + Связи требований
2. **Фаза 2:** Комментарии + Тест-кейсы + Улучшение существующих сущностей
3. **Фаза 3:** Документация + Риски + Метрики
4. **Фаза 4:** Развертывание + Интеграции + Дополнительные функции

### Миграция данных:
- Создать скрипты миграции для добавления новых полей
- Сохранить обратную совместимость с существующими данными
- Добавить значения по умолчанию для новых полей

### Производительность:
- Добавить индексы на часто используемые поля
- Рассмотреть партиционирование для больших таблиц (change_history)
- Использовать материализованные представления для метрик

---

## 🔍 Дополнительные соображения

### Безопасность:
- Шифрование чувствительных данных (API токены, пароли)
- Аудит всех изменений
- Ограничение доступа на уровне строк (Row Level Security)

### Масштабируемость:
- Рассмотреть использование JSONB для гибких структур
- Кэширование часто запрашиваемых данных
- Архивация старых данных

### Интеграции:
- API для интеграции с внешними системами
- Webhooks для уведомлений о событиях
- Экспорт в различные форматы

