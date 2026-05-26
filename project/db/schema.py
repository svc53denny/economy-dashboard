import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "economy.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS news (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT    NOT NULL,
            url          TEXT    UNIQUE NOT NULL,
            source       TEXT,
            published_at TEXT,
            summary      TEXT,
            fetched_at   TEXT    DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS market_data (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol      TEXT    NOT NULL,
            name        TEXT,
            price       REAL,
            change_pct  REAL,
            volume      REAL,
            fetched_at  TEXT    DEFAULT (datetime('now','localtime'))
        );
        CREATE INDEX IF NOT EXISTS idx_news_fetched   ON news(fetched_at DESC);
        CREATE INDEX IF NOT EXISTS idx_market_sym_time ON market_data(symbol, fetched_at DESC);
    """)
    conn.commit()
    conn.close()
