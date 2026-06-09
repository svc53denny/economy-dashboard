import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock, patch
import db.helpers as helpers_mod


def _sb_mock(rows=None):
    """Supabase 클라이언트 체인 mock 생성."""
    chain = MagicMock()
    chain.execute.return_value = MagicMock(data=rows or [])
    for method in ("select", "insert", "update", "upsert", "eq", "is_", "order", "limit"):
        getattr(chain, method).return_value = chain
    sb = MagicMock()
    sb.table.return_value = chain
    return sb, chain


def test_insert_news_calls_upsert():
    sb, chain = _sb_mock()
    with patch("db.helpers.get_supabase", return_value=sb):
        helpers_mod.insert_news("테스트 뉴스", "https://ex.com/1", "소스A", "2024-01-01")
    sb.table.assert_called_with("items")
    chain.upsert.assert_called_once()
    upsert_data = chain.upsert.call_args[0][0]
    assert upsert_data["type"] == "news"
    assert upsert_data["url"] == "https://ex.com/1"
    assert upsert_data["title"] == "테스트 뉴스"


def test_insert_news_ignores_duplicate():
    sb, chain = _sb_mock()
    with patch("db.helpers.get_supabase", return_value=sb):
        helpers_mod.insert_news("뉴스A", "https://ex.com/dup", "소스", "2024-01-01")
        helpers_mod.insert_news("뉴스B", "https://ex.com/dup", "소스", "2024-01-01")
    kwargs = chain.upsert.call_args_list[0][1]
    assert kwargs.get("ignore_duplicates") is True


def test_update_news_summary():
    sb, chain = _sb_mock()
    with patch("db.helpers.get_supabase", return_value=sb):
        helpers_mod.update_news_summary("https://ex.com/1", "AI 요약 결과")
    chain.update.assert_called_once_with({"summary": "AI 요약 결과"})


def test_get_recent_news_returns_data():
    rows = [{"id": 1, "type": "news", "title": "제목", "url": "https://ex.com/1"}]
    sb, chain = _sb_mock(rows)
    with patch("db.helpers.get_supabase", return_value=sb):
        data = helpers_mod.get_recent_news(limit=10)
    assert data == rows
    chain.eq.assert_any_call("type", "news")


def test_get_unsummarized_news_filters_null():
    sb, chain = _sb_mock()
    with patch("db.helpers.get_supabase", return_value=sb):
        helpers_mod.get_unsummarized_news(limit=5)
    chain.is_.assert_called_once_with("summary", "null")


def test_upsert_market_data():
    sb, chain = _sb_mock()
    with patch("db.helpers.get_supabase", return_value=sb):
        helpers_mod.upsert_market_data("^KS11", "KOSPI", 2700.0, 1.2, 500000)
    sb.table.assert_called_with("items")
    insert_data = chain.insert.call_args[0][0]
    assert insert_data["type"] == "market"
    assert insert_data["symbol"] == "^KS11"
    assert insert_data["price"] == 2700.0


def test_get_latest_market_data_deduplicates():
    rows = [
        {"id": 10, "symbol": "^KS11", "name": "KOSPI",  "price": 2720.0, "change_pct": 0.8},
        {"id":  5, "symbol": "^KS11", "name": "KOSPI",  "price": 2700.0, "change_pct": 1.2},
        {"id":  9, "symbol": "^KQ11", "name": "KOSDAQ", "price": 850.0,  "change_pct": 0.5},
    ]
    sb, chain = _sb_mock(rows)
    with patch("db.helpers.get_supabase", return_value=sb):
        data = helpers_mod.get_latest_market_data()
    assert len(data) == 2
    kospi = next(d for d in data if d["symbol"] == "^KS11")
    assert kospi["price"] == 2720.0
