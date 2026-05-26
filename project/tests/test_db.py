import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db.schema as schema_mod
import db.helpers as helpers_mod
from db.schema import init_db
from db.helpers import (
    insert_news, get_recent_news, get_unsummarized_news,
    update_news_summary, upsert_market_data, get_latest_market_data,
)


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test.db")
    monkeypatch.setattr(schema_mod,  "DB_PATH", test_db)
    monkeypatch.setattr(helpers_mod, "DB_PATH", test_db)
    init_db()


def test_insert_and_retrieve():
    insert_news("테스트 뉴스", "https://ex.com/1", "소스A", "2024-01-01")
    news = get_recent_news(limit=10)
    assert len(news) == 1
    assert news[0]["title"] == "테스트 뉴스"


def test_duplicate_url_ignored():
    insert_news("뉴스 A", "https://ex.com/dup", "소스", "2024-01-01")
    insert_news("뉴스 B", "https://ex.com/dup", "소스", "2024-01-01")
    assert len(get_recent_news()) == 1


def test_unsummarized_then_summarized():
    insert_news("요약 대상", "https://ex.com/2", "소스", "2024-01-01")
    assert len(get_unsummarized_news()) == 1
    update_news_summary("https://ex.com/2", "AI 요약 결과")
    assert len(get_unsummarized_news()) == 0


def test_market_data_upsert_and_latest():
    upsert_market_data("^KS11", "KOSPI", 2700.0, 1.2, 500000)
    upsert_market_data("^KS11", "KOSPI", 2720.0, 0.8, 600000)
    data = get_latest_market_data()
    assert len(data) == 1
    assert data[0]["price"] == 2720.0
