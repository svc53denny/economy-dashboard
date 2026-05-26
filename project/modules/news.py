import feedparser
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

RSS_FEEDS = [
    ("Reuters Business",  "https://feeds.reuters.com/reuters/businessNews"),
    ("CNN Money",         "http://rss.cnn.com/rss/money_topstories.rss"),
    ("연합뉴스 경제",       "https://www.yna.co.kr/rss/economy.xml"),
    ("한국경제",           "https://rss.hankyung.com/economy.xml"),
]


def fetch_all_news() -> list[dict]:
    articles = []
    for source, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                title = entry.get("title", "").strip()
                link  = entry.get("link", "").strip()
                published = entry.get("published", datetime.now().isoformat())
                if title and link:
                    articles.append({
                        "title":        title,
                        "url":          link,
                        "source":       source,
                        "published_at": published,
                    })
        except Exception as e:
            logger.warning("피드 수집 실패 [%s]: %s", source, e)
    return articles
