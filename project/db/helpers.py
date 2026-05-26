import sqlite3
from contextlib import contextmanager
from db.schema import DB_PATH


@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def insert_news(title: str, url: str, source: str, published_at: str) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO news (title, url, source, published_at) VALUES (?,?,?,?)",
            (title, url, source, published_at),
        )


def update_news_summary(url: str, summary: str) -> None:
    with _conn() as conn:
        conn.execute("UPDATE news SET summary=? WHERE url=?", (summary, url))


def get_recent_news(limit: int = 30) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM news ORDER BY fetched_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_unsummarized_news(limit: int = 5) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM news WHERE summary IS NULL ORDER BY fetched_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def upsert_market_data(symbol: str, name: str, price: float, change_pct: float, volume: float) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT INTO market_data (symbol, name, price, change_pct, volume) VALUES (?,?,?,?,?)",
            (symbol, name, price, change_pct, volume),
        )


def get_latest_market_data() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("""
            SELECT m.*
            FROM market_data m
            INNER JOIN (
                SELECT symbol, MAX(id) AS max_id
                FROM market_data GROUP BY symbol
            ) latest ON m.id = latest.max_id
            ORDER BY m.name
        """).fetchall()
    return [dict(r) for r in rows]
