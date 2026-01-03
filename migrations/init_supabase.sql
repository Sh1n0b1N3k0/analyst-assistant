-- Инициализация Supabase для локальной разработки
-- Выполнить после первого запуска docker-compose

-- Включить расширения
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- Создать схему prompts (если еще не создана)
CREATE SCHEMA IF NOT EXISTS prompts;

-- Выполнить миграцию промптов
\i create_prompts_schema.sql

-- Создать базовые таблицы для системы (на основе ER-диаграммы)
-- TODO: Добавить создание всех таблиц из ER_Main.wsd

