# 🇪🇸 Spanish Verb Conjugation Game Bot

![Python](https://img.shields.io/badge/Python-3.x-blue)
![aiogram](https://img.shields.io/badge/aiogram-3.0-yellowgreen)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey)

## 📚 Описание

Этот проект — интерактивная игра в Telegram для изучения и практики спряжения испанских глаголов. Пользователи могут улучшать свои знания испанского языка, угадывая правильные формы глаголов в различных временах. Бот не только проверяет правильность ответа, но и предоставляет примеры использования глагола в контексте.

## 🚀 Функционал

- **Игра без остановок** — бот автоматически начинает новую игру после каждого ответа.
- **Примеры предложений** — после каждого ответа предоставляется пример использования глагола.
- **Многообразие времен** — все основные времена испанского языка в одной игре.
- **Поддержка FSM** — бот сохраняет состояние игры для каждого пользователя.

## 🛠️ Установка

1. Склонируйте репозиторий:

    ```bash
    git clone https://github.com/yourusername/spanish-verb-game-bot.git
    cd spanish-verb-game-bot
    ```

2. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

3. Создайте и настройте базу данных:

    Убедитесь, что ваша база данных `verbs.db` настроена правильно и содержит все необходимые таблицы (`verbs`, `tenses`, `subjects`, `verb_forms`, `examples`). Вы можете загрузить данные из CSV-файла или использовать свой набор данных.

4. Настройте переменные окружения:

    Убедитесь, что вы задали свой токен Telegram API:

    ```bash
    export TELEGRAM_BOT_TOKEN='YOUR_TELEGRAM_BOT_TOKEN'
    ```

5. Запустите бота:

    ```bash
    python bot.py
    ```

## 📁 Structure of the project

spanish_verbs/
├── .github/
│   └── workflows/
│       └── pylint.yml          # github workflow to linter Python code
├── data/
│   └── imperativo.csv          # CSV база данных с глаголами и примерами
│   └── list_of_verbs.txt       # Список 50 самых популярных испанских глаголов
│   └── verbs.db                # SQLite база данных с глаголами и примерами
├── bot.py                      # Основной файл бота
├── requirements.txt            # Зависимости проекта
├── README.md                   # Документация проекта
└── tests/
    └── test_bot.py             # Тесты для бота (на pytest)
