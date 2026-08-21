import os
import sqlite3
from contextlib import contextmanager


DB_DIR = os.getenv("DB_DIR", "db")
KARMA_DB = os.path.join(DB_DIR, "karma.db")
QUOTES_DB = os.path.join(DB_DIR, "quotes.db")


def initialize_databases() -> None:
    os.makedirs(DB_DIR, exist_ok=True)
    with sqlite3.connect(KARMA_DB) as database:
        database.execute(
            """
            CREATE TABLE IF NOT EXISTS karma (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                palabra TEXT NOT NULL COLLATE NOCASE,
                karmavalue INTEGER NOT NULL DEFAULT 0,
                isuser TEXT NOT NULL DEFAULT 'NO',
                karmagiven INTEGER NOT NULL DEFAULT 0
            )
            """
        )
    with sqlite3.connect(QUOTES_DB) as database:
        database.execute(
            """
            CREATE TABLE IF NOT EXISTS quotes (
                quote TEXT NOT NULL,
                username TEXT NOT NULL,
                date TEXT NOT NULL
            )
            """
        )


@contextmanager
def karma_database():
    database = sqlite3.connect(KARMA_DB, timeout=10)
    try:
        yield database
        database.commit()
    finally:
        database.close()
