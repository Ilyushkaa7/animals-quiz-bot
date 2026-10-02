# Animals Quiz Bot

A learning project built with Python and aiogram: a Telegram quiz with animal clues, multiple-choice answers, hints, lives and scores.

## Features

- Random animal facts
- Three clues and multiple-choice answers
- Lives, scores and a letter-reveal hint
- Inline navigation
- Local JSON persistence

## Run locally

```sh
git clone https://github.com/Ilyushkaa7/animals-quiz-bot.git
cd animals-quiz-bot
python -m venv .venv
```

Activate the environment (`.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on Linux/macOS), then install dependencies:

```sh
python -m pip install -r requirements.txt
```

Create a local `.env` file:

```dotenv
BOT_TOKEN=your_telegram_bot_token
```

Start the bot:

```sh
python animal_bot.py
```

The bot needs a Telegram bot token and an internet connection. Keep `.env` and `users.json` out of Git; both are ignored.

## Structure

- `animal_bot.py` — handlers and polling entry point
- `animals_data.py` — animals and clues
- `keyboards.py` — reply and inline keyboards
- `database.py` — local JSON state
- `requirements.txt` — dependencies

## Limitations

This is an educational prototype. The JSON store rewrites the whole file on updates and is not designed for multiple bot processes. SQLite storage, stale-button handling and automated tests are possible next steps.
