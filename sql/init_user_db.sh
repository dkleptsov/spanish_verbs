#!/bin/bash

# Create a new PostgreSQL database using the provided environment variable $DB_NAME.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE $DB_NAME;
EOSQL

# Now, the script switches to the newly created database ($DB_NAME) and proceeds with further setup.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" <<-EOSQL
    -- Step 1: Create the raw table for storing verb forms. This table will temporarily store data before normalization.
    -- Each row represents a unique combination of verb, tense, and subject.
    CREATE TABLE IF NOT EXISTS verb_form_raw (
        id SERIAL PRIMARY KEY,           -- Unique identifier for each verb form entry
        verb VARCHAR(50) NOT NULL,       -- The verb in infinitive form (e.g., "hablar")
        tense VARCHAR(50) NOT NULL,      -- The tense of the verb (e.g., "Present")
        subject VARCHAR(50) NOT NULL,    -- The subject performing the action (e.g., "yo", "tú")
        form VARCHAR(50),                -- The conjugated form of the verb (e.g., "hablo")
        example VARCHAR(256) NOT NULL,   -- An example sentence using the verb form
        verb_id INTEGER,                 -- Foreign key to the normalized 'verb' table (set later)
        tense_id INTEGER,                -- Foreign key to the normalized 'tense' table (set later)
        subject_id INTEGER,              -- Foreign key to the normalized 'subject' table (set later)
        UNIQUE (verb_id, tense_id, subject_id) -- Ensure each combination of verb, tense, and subject is unique
    );

    -- Step 2: Import verb data from a CSV file (located at /docker-entrypoint-initdb.d/sql/imperativo.csv).
    -- This file contains initial verb forms that will be processed later.
    COPY verb_form_raw (verb,tense,subject,form,example)
    FROM '/docker-entrypoint-initdb.d/imperativo.csv'
    WITH (
        FORMAT csv,             -- CSV format
        HEADER true,            -- The first row of the CSV file contains headers
        DELIMITER ',',          -- Comma is used as the delimiter
        NULL ''                 -- Empty fields are interpreted as NULL
    );

    -- Step 3: Create lookup tables to normalize the data and reduce redundancy.
    -- Each lookup table stores unique entries for verbs, tenses, and subjects.
    CREATE TABLE verb (
        id SERIAL PRIMARY KEY,         -- Unique identifier for each verb
        name VARCHAR(128) UNIQUE       -- The verb in infinitive form (e.g., "hablar")
    );
    CREATE TABLE tense (
        id SERIAL PRIMARY KEY,         -- Unique identifier for each tense
        name VARCHAR(128) UNIQUE       -- Name of the tense (e.g., "Present")
    );
    CREATE TABLE subject (
        id SERIAL PRIMARY KEY,         -- Unique identifier for each subject
        name VARCHAR(128) UNIQUE       -- The subject (e.g., "yo", "tú")
    );

    -- Step 4: Populate the lookup tables with unique values from the raw verb form table.
    INSERT INTO verb (name) SELECT DISTINCT verb FROM verb_form_raw;
    INSERT INTO tense (name) SELECT DISTINCT tense FROM verb_form_raw;
    INSERT INTO subject (name) SELECT DISTINCT subject FROM verb_form_raw;

    -- Step 5: Update the raw verb form table to reference the normalized tables.
    -- These statements assign the appropriate foreign key IDs (verb_id, tense_id, subject_id) to each row.
    UPDATE verb_form_raw SET verb_id = (SELECT verb.id FROM verb WHERE verb.name = verb_form_raw.verb);
    UPDATE verb_form_raw SET tense_id = (SELECT tense.id FROM tense WHERE tense.name = verb_form_raw.tense);
    UPDATE verb_form_raw SET subject_id = (SELECT subject.id FROM subject WHERE subject.name = verb_form_raw.subject);

    -- Step 6: Rename the raw table and drop redundant columns (verb, tense, subject) that have been normalized.
    -- After this step, the verb form table will store only foreign key references.
    ALTER TABLE verb_form_raw
    DROP COLUMN verb,
    DROP COLUMN tense,
    DROP COLUMN subject;

    -- Step 7: Add foreign key constraints to ensure referential integrity between verb_form and the lookup tables.
    ALTER TABLE verb_form_raw ADD FOREIGN KEY (verb_id) REFERENCES verb(id) ON DELETE CASCADE;
    ALTER TABLE verb_form_raw ADD FOREIGN KEY (tense_id) REFERENCES tense(id) ON DELETE CASCADE;
    ALTER TABLE verb_form_raw ADD FOREIGN KEY (subject_id) REFERENCES subject(id) ON DELETE CASCADE;

    -- Step 8: Rename the verb_form_raw table to its final form: verb_form.
    ALTER TABLE verb_form_raw RENAME TO verb_form;

    -- Step 9: Create a new user with specific database privileges.
    CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_USER_PASSWORD';
    GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
    GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;

EOSQL
