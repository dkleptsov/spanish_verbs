-- ==========================================================
-- SQL script to import data from a CSV file into PostgreSQL
-- ==========================================================

-- Step 1: Create the target table if it doesn't already exist
-- This table will store the imported data from the CSV file
CREATE TABLE IF NOT EXISTS verb_form_raw (
    id SERIAL PRIMARY KEY,           -- Unique identifier for each verb form
    verb VARCHAR(50) NOT NULL,       -- Verb in Infinitivo
    tense VARCHAR(50) NOT NULL,      -- Name of the tense
    subject VARCHAR(50) NOT NULL,    -- Type of the subject
    form VARCHAR(50),                -- Correspondent verb form
    example VARCHAR(256) NOT NULL,   -- Example sentence with this verb form
    verb_id INTEGER,                 -- Unique identifier for each verb
    tense_id INTEGER,                -- Unique identifier for each tense
    subject_id INTEGER,              -- Unique identifier for each subject
    UNIQUE (verb_id, tense_id, subject_id)
);

-- Step 2: Copy data from the CSV file into the target table
-- The CSV file should be located in a directory accessible by the database server
-- Adjust the file path and delimiter according to your CSV file's location and structure
COPY verb_form_raw (verb,tense,subject,form,example)
FROM 'data/imperativo.csv'  -- Path to CSV file
WITH (
    FORMAT csv,             -- Specify the file format as CSV
    HEADER true,            -- The first row in the CSV file contains column headers
    DELIMITER ',',          -- The delimiter used in the CSV file (comma in this case)
    NULL ''                 -- Specify how NULL values are represented (empty string here)
);
-- OR
\COPY verb_form_raw (verb,tense,subject,form,example)
FROM 'data/imperativo.csv'  -- Path to CSV file
WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '');

-- Step 3: Verify that the data has been imported correctly
-- This query retrieves the first 10 chars from the text fields
SELECT
    id,
    SUBSTRING(verb FROM 1 FOR 10) AS verb,
    SUBSTRING(tense FROM 1 FOR 10) AS tense,
    SUBSTRING(subject FROM 1 FOR 10) AS subject,
    SUBSTRING(form FROM 1 FOR 10) AS form,
    SUBSTRING(example FROM 1 FOR 10) AS example,
    verb_id,
    tense_id,
    subject_id
FROM verb_form_raw ORDER BY id;

-- Step 4: Create look up tables for each column that can be separated.
-- To elimininate vertical replication.
CREATE TABLE verb (
  id SERIAL PRIMARY KEY,         -- Unique identifier for each verb form.
  name VARCHAR(128) UNIQUE       -- Verb in infinitivo.
);

CREATE TABLE tense (
  id SERIAL PRIMARY KEY,         -- Unique identifier for each verb form.
  name VARCHAR(128) UNIQUE       -- Name of the tense.
);

CREATE TABLE subject (
  id SERIAL PRIMARY KEY,         -- Unique identifier for each verb form.
  name VARCHAR(128) UNIQUE       -- Name of the subject.
);

-- Step 5: Insert unique values from correspondent column.
-- To populate each look up table.
INSERT INTO verb (name) SELECT DISTINCT verb FROM verb_form_raw;

INSERT INTO tense (name) SELECT DISTINCT tense FROM verb_form_raw;

INSERT INTO subject (name) SELECT DISTINCT subject FROM verb_form_raw;

-- Step 5: Populate id columns in verb_form_raw.
-- For this we will get ids from look up tables.
UPDATE verb_form_raw SET verb_id = (SELECT verb.id FROM verb WHERE verb.name = verb_form_raw.verb);
UPDATE verb_form_raw SET tense_id = (SELECT tense.id FROM tense WHERE tense.name = verb_form_raw.tense);
UPDATE verb_form_raw SET subject_id = (SELECT subject.id FROM subject WHERE subject.name = verb_form_raw.subject);

-- Step 5: Rename the table and drop redundant columns.
-- And print final result to check everything is according to plan.
ALTER TABLE verb_form_raw
DROP COLUMN verb,
DROP COLUMN tense,
DROP COLUMN subject;

ALTER TABLE verb_form_raw ADD FOREIGN KEY (verb_id) REFERENCES verb(id) ON DELETE CASCADE;
ALTER TABLE verb_form_raw ADD FOREIGN KEY (tense_id) REFERENCES tense(id) ON DELETE CASCADE;
ALTER TABLE verb_form_raw ADD FOREIGN KEY (subject_id) REFERENCES subject(id) ON DELETE CASCADE;

ALTER TABLE verb_form_raw RENAME TO verb_form;

SELECT * FROM verb_form ORDER BY id;

-- Step 5: Lets reconstruct original view from CSV file.
-- And print final result to check everything is according to plan.
SELECT verb.name as verb, 
       tense.name as tense, 
       subject.name as subject, 
       verb_form.form, verb_form.example
FROM verb_form
JOIN verb ON verb.id=verb_form.verb_id
JOIN tense ON tense.id=verb_form.tense_id
JOIN subject ON subject.id=verb_form.subject_id
ORDER BY verb_form.id;

-- End of SQL Script
