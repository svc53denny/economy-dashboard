from db.supabase_client import get_supabase


def insert_news(title: str, url: str, source: str, published_at: str) -> None:
    get_supabase().table("items").upsert(
        {"type": "news", "title": title, "url": url,
         "source": source, "published_at": published_at},
        on_conflict="url",
        ignore_duplicates=True,
    ).execute()


def update_news_summary(url: str, summary: str) -> None:
    get_supabase().table("items").update(
        {"summary": summary}
    ).eq("type", "news").eq("url", url).execute()


def get_recent_news(limit: int = 30) -> list[dict]:
    res = (
        get_supabase()
        .table("items")
        .select("*")
        .eq("type", "news")
        .order("fetched_at", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data


def get_unsummarized_news(limit: int = 5) -> list[dict]:
    res = (
        get_supabase()
        .table("items")
        .select("*")
        .eq("type", "news")
        .is_("summary", "null")
        .order("fetched_at", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data


def upsert_market_data(
    symbol: str, name: str, price: float, change_pct: float, volume: float
) -> None:
    get_supabase().table("items").insert(
        {"type": "market", "symbol": symbol, "name": name,
         "price": price, "change_pct": change_pct, "volume": volume}
    ).execute()


def get_latest_market_data() -> list[dict]:
    res = (
        get_supabase()
        .table("items")
        .select("*")
        .eq("type", "market")
        .order("id", desc=True)
        .execute()
    )
    seen: set[str] = set()
    latest: list[dict] = []
    for row in res.data:
        sym = row.get("symbol") or ""
        if sym and sym not in seen:
            seen.add(sym)
            latest.append(row)
    latest.sort(key=lambda x: x.get("name") or "")
    return latest
