-- ============================================================
-- HR Analytics Platform — Seed pattern (MySQL dialect)
-- The Python pipeline (src/database.py) seeds data programmatically
-- from data/processed/employees_clean.csv and skips existing
-- employee_ids. This file documents the equivalent raw-SQL pattern
-- if you prefer to load via `LOAD DATA INFILE` + MySQL CLI instead.
-- ============================================================

USE hr_analytics;

-- Example of safe duplicate-tolerant insert (used conceptually by the
-- Python layer; also copy-pasteable for manual single-row upserts):
INSERT INTO employees (
    employee_id, department, region, education, gender, recruitment_channel,
    no_of_trainings, age, previous_year_rating, length_of_service,
    KPIs_met_more_than_80, awards_won, avg_training_score
)
VALUES (
    :employee_id, :department, :region, :education, :gender, :recruitment_channel,
    :no_of_trainings, :age, :previous_year_rating, :length_of_service,
    :KPIs_met_more_than_80, :awards_won, :avg_training_score
)
ON DUPLICATE KEY UPDATE
    department = VALUES(department),
    region = VALUES(region),
    education = VALUES(education),
    gender = VALUES(gender),
    recruitment_channel = VALUES(recruitment_channel),
    no_of_trainings = VALUES(no_of_trainings),
    age = VALUES(age),
    previous_year_rating = VALUES(previous_year_rating),
    length_of_service = VALUES(length_of_service),
    KPIs_met_more_than_80 = VALUES(KPIs_met_more_than_80),
    awards_won = VALUES(awards_won),
    avg_training_score = VALUES(avg_training_score);

-- Bulk load example (adjust path; requires local_infile enabled):
-- LOAD DATA LOCAL INFILE 'data/processed/employees_clean.csv'
-- INTO TABLE employees
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS;
