import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)
_scheduler: BackgroundScheduler | None = None


def _collect_news() -> None:
    from modules.news import fetch_all_news
    from modules.summarizer import summarize
    from db.helpers import insert_news, get_unsummarized_news, update_news_summary

    articles = fetch_all_news()
    for a in articles:
        insert_news(a["title"], a["url"], a["source"], a["published_at"])
    logger.info("뉴스 수집 완료: %d건", len(articles))

    for item in get_unsummarized_news(limit=5):
        summary = summarize(item["title"])
        if summary:
            update_news_summary(item["url"], summary)


def _collect_market() -> None:
    from modules.market import fetch_market_data
    from db.helpers import upsert_market_data

    data = fetch_market_data()
    for d in data:
        upsert_market_data(d["symbol"], d["name"], d["price"], d["change_pct"], d["volume"])
    logger.info("시장 데이터 갱신: %d종목", len(data))


def start_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    _scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    _scheduler.add_job(_collect_news,   IntervalTrigger(minutes=10), id="news",   replace_existing=True)
    _scheduler.add_job(_collect_market, IntervalTrigger(minutes=10), id="market", replace_existing=True)
    _scheduler.start()

    # 최초 실행
    _collect_market()
    _collect_news()
    logger.info("스케줄러 시작 완료")


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
