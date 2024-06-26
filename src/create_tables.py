import sqlite3

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

if __name__ == '__main__':
    db_name = 'data/verbs.db'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    create_tables(cursor)
    conn.close()
