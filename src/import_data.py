import sqlite3
import csv

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
    db_name = 'data/verbs.db'
    csv_file = 'data/test_data.csv'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    import_data_from_csv(cursor, csv_file)
    conn.close()
