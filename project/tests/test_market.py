import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from modules.market import fetch_market_data


def _make_fast_info(price=3000.0, prev=2950.0, volume=1_000_000):
    info = MagicMock()
    info.last_price      = price
    info.previous_close  = prev
    info.three_month_average_volume = volume
    return info


def test_returns_market_list():
    mock_ticker = MagicMock()
    mock_ticker.fast_info = _make_fast_info()
    with patch("modules.market.yf.Ticker", return_value=mock_ticker):
        data = fetch_market_data()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all({"symbol", "name", "price", "change_pct"} <= set(d) for d in data)


def test_change_pct_calculated():
    mock_ticker = MagicMock()
    mock_ticker.fast_info = _make_fast_info(price=3100.0, prev=3000.0)
    with patch("modules.market.yf.Ticker", return_value=mock_ticker):
        data = fetch_market_data()
    assert any(abs(d["change_pct"] - 3.33) < 0.1 for d in data)


def test_failed_symbol_skipped():
    with patch("modules.market.yf.Ticker", side_effect=Exception("API error")):
        data = fetch_market_data()
    assert data == []
