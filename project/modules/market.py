import yfinance as yf
import requests
import logging

logger = logging.getLogger(__name__)

_FEAR_GREED_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
_FEAR_GREED_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer":         "https://edition.cnn.com/markets/fear-and-greed",
    "Origin":          "https://edition.cnn.com",
}


def fetch_fear_greed() -> dict | None:
    try:
        resp = requests.get(_FEAR_GREED_URL, headers=_FEAR_GREED_HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()["fear_and_greed"]
        return {
            "score":        round(float(data["score"]), 1),
            "rating":       data["rating"],
            "prev_close":   round(float(data["previous_close"]), 1),
            "prev_1_week":  round(float(data["previous_1_week"]), 1),
            "prev_1_month": round(float(data["previous_1_month"]), 1),
        }
    except Exception as e:
        logger.warning("Fear & Greed 수집 실패: %s", e)
        return None

SYMBOLS: dict[str, str] = {
    "^KS11":  "KOSPI",
    "^KQ11":  "KOSDAQ",
    "^GSPC":  "S&P 500",
    "^IXIC":  "NASDAQ",
    "^DJI":   "Dow Jones",
    "KRW=X":  "USD/KRW",
    "GC=F":   "Gold",
    "CL=F":   "WTI Oil",
}


def fetch_market_data() -> list[dict]:
    results = []
    for symbol, name in SYMBOLS.items():
        try:
            info = yf.Ticker(symbol).fast_info
            price      = float(info.last_price or 0)
            prev_close = float(info.previous_close or price)
            change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0.0
            volume     = float(getattr(info, "three_month_average_volume", 0) or 0)
            results.append({
                "symbol":     symbol,
                "name":       name,
                "price":      round(price, 2),
                "change_pct": round(change_pct, 2),
                "volume":     volume,
            })
        except Exception as e:
            logger.warning("시장 데이터 수집 실패 [%s]: %s", symbol, e)
    return results
