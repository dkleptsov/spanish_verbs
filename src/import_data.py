import sqlite3
import csv


CSV_PATH = "data/imperativo.csv"
DB_PATH = "data/imperativo.db"


def create_tables(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verbs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verb TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tense TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verb_forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verb_id INTEGER NOT NULL,
            tense_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            form TEXT NOT NULL,
            FOREIGN KEY (verb_id) REFERENCES verbs(id),
            FOREIGN KEY (tense_id) REFERENCES tenses(id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS examples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verb_form_id INTEGER NOT NULL,
            example TEXT NOT NULL,
            FOREIGN KEY (verb_form_id) REFERENCES verb_forms(id)
        )
    ''')

    cursor.connection.commit()


def import_data_from_csv(cursor, csv_file):
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]

    verbs = {row['verb'] for row in data}
    tenses = {row['tense'] for row in data}
    subjects = {row['subject'] for row in data}

    cursor.executemany('INSERT INTO verbs (verb) VALUES (?)', [(verb,) for verb in verbs])
    cursor.executemany('INSERT INTO tenses (tense) VALUES (?)', [(tense,) for tense in tenses])
    cursor.executemany('INSERT INTO subjects (subject) VALUES (?)', [(subject,) for subject in subjects])

    cursor.connection.commit()

    cursor.execute('SELECT id, verb FROM verbs')
    verb_ids = {verb: id for id, verb in cursor.fetchall()}

    cursor.execute('SELECT id, tense FROM tenses')
    tense_ids = {tense: id for id, tense in cursor.fetchall()}

    cursor.execute('SELECT id, subject FROM subjects')
    subject_ids = {subject: id for id, subject in cursor.fetchall()}

    verb_forms_data = [
        (verb_ids[row['verb']], tense_ids[row['tense']], subject_ids[row['subject']], row['form'])
        for row in data
    ]
    cursor.executemany('''
        INSERT INTO verb_forms (verb_id, tense_id, subject_id, form)
        VALUES (?, ?, ?, ?)
    ''', verb_forms_data)

    cursor.connection.commit()

    cursor.execute('SELECT id, verb_id, tense_id, subject_id, form FROM verb_forms')
    verb_form_ids = {
        (verb_id, tense_id, subject_id, form): id
        for id, verb_id, tense_id, subject_id, form in cursor.fetchall()
    }

    examples_data = [
        (verb_form_ids[(verb_ids[row['verb']], tense_ids[row['tense']], subject_ids[row['subject']], row['form'])], row['example'])
        for row in data
    ]
    cursor.executemany('''
        INSERT INTO examples (verb_form_id, example)
        VALUES (?, ?)
    ''', examples_data)

    cursor.connection.commit()

if __name__ == '__main__':
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    create_tables(cursor)
    import_data_from_csv(cursor, CSV_PATH)
    conn.close()
