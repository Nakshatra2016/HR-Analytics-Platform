-- ============================================================
-- HR Analytics Platform — Database Schema (MySQL dialect)
-- The Python app creates this automatically via src/database.py
-- for both SQLite and MySQL; this file is kept for reference,
-- manual inspection, and use with MySQL Workbench / CLI.
-- ============================================================

CREATE DATABASE IF NOT EXISTS hr_analytics;
USE hr_analytics;

CREATE TABLE IF NOT EXISTS employees (
    employee_id            INT UNSIGNED PRIMARY KEY,
    department              VARCHAR(100) NOT NULL,
    region                   VARCHAR(100) NOT NULL,
    education                VARCHAR(100) NOT NULL,
    gender                   CHAR(1)      NOT NULL,
    recruitment_channel      VARCHAR(100) NOT NULL,
    no_of_trainings          TINYINT UNSIGNED NOT NULL,
    age                      TINYINT UNSIGNED NOT NULL,
    previous_year_rating     TINYINT UNSIGNED,
    length_of_service        TINYINT UNSIGNED NOT NULL,
    KPIs_met_more_than_80    TINYINT(1) NOT NULL DEFAULT 0,
    awards_won               TINYINT(1) NOT NULL DEFAULT 0,
    avg_training_score       TINYINT UNSIGNED NOT NULL,

    CONSTRAINT chk_age CHECK (age BETWEEN 18 AND 70),
    CONSTRAINT chk_rating CHECK (previous_year_rating BETWEEN 1 AND 5),
    CONSTRAINT chk_score CHECK (avg_training_score BETWEEN 0 AND 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_department ON employees(department);
CREATE INDEX idx_region ON employees(region);
CREATE INDEX idx_gender ON employees(gender);
CREATE INDEX idx_rating ON employees(previous_year_rating);
