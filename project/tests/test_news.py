import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from modules.news import fetch_all_news


def _make_mock_feed(entries):
    feed = MagicMock()
    feed.entries = entries
    return feed


def _make_entry(title="테스트 뉴스", link="https://ex.com/news"):
    entry = MagicMock()
    entry.get.side_effect = lambda k, d=None: {
        "title": title, "link": link, "published": "Mon, 01 Jan 2024 00:00:00 GMT"
    }.get(k, d)
    return entry


def test_returns_articles():
    mock_feed = _make_mock_feed([_make_entry()])
    with patch("modules.news.feedparser.parse", return_value=mock_feed):
        articles = fetch_all_news()
    assert isinstance(articles, list)
    assert len(articles) > 0
    assert all({"title", "url", "source", "published_at"} <= set(a) for a in articles)


def test_failed_feed_skipped():
    with patch("modules.news.feedparser.parse", side_effect=Exception("timeout")):
        articles = fetch_all_news()
    assert articles == []


def test_empty_title_filtered():
    bad  = _make_entry(title="",  link="https://ex.com/bad")
    good = _make_entry(title="정상 뉴스", link="https://ex.com/good")
    mock_feed = _make_mock_feed([bad, good])
    with patch("modules.news.feedparser.parse", return_value=mock_feed):
        articles = fetch_all_news()
    titles = [a["title"] for a in articles]
    assert "" not in titles
