import sqlite3
import random

def get_random_verb_form(cursor):
    cursor.execute('''
        SELECT verb_forms.id, verbs.verb, tenses.tense, subjects.subject, verb_forms.form
        FROM verb_forms
        JOIN verbs ON verb_forms.verb_id = verbs.id
        JOIN tenses ON verb_forms.tense_id = tenses.id
        JOIN subjects ON verb_forms.subject_id = subjects.id
        ORDER BY RANDOM() LIMIT 1
    ''')
    return cursor.fetchone()

def play_game(cursor):
    print("Угадай форму глагола на испанском!")
    while True:
        verb_form = get_random_verb_form(cursor)
        if not verb_form:
            print("Нет данных для игры.")
            break

        verb_form_id, verb, tense, subject, form = verb_form
        print(f"Глагол: {verb}, Время: {tense}, Местоимение: {subject}")
        user_input = input("Введите правильную форму: ").strip()

        if user_input.lower() == form.lower():
            print("Правильно!")
        else:
            print(f"Неправильно. Правильный ответ: {form}")


if __name__ == '__main__':
    db_name = 'data/verbs.db'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    play_game(cursor)
    conn.close()