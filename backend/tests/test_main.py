from unittest.mock import MagicMock, PropertyMock, patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def _mock_hist(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    index = pd.to_datetime([r["date"] for r in rows], utc=True).tz_convert("Asia/Tokyo")
    df = pd.DataFrame(rows, index=index)
    df.index.name = "Date"
    return df.drop(columns=["date"])


def _mock_ticker(rows: list[dict], info: dict = {}):
    m = MagicMock()
    m.history.return_value = _mock_hist(rows)
    m.info = info
    return m


SAMPLE_ROWS = [
    {"date": "2026-01-05", "Open": 3411.0, "High": 3455.0, "Low": 3397.0, "Close": 3399.0, "Volume": 18505900},
    {"date": "2026-01-06", "Open": 3488.0, "High": 3504.0, "Low": 3423.0, "Close": 3429.0, "Volume": 21996200},
]

SAMPLE_INFO = {
    "longName": "Toyota Motor Corporation",
    "shortName": "Toyota",
    "sector": "Consumer Cyclical",
    "exchange": "JPX",
    "quoteType": "EQUITY",
}


class TestGetStockPrices:
    def test_returns_ohlcv(self):
        with patch("main.yf.Ticker", return_value=_mock_ticker(SAMPLE_ROWS)):
            r = client.get("/api/stock/7203")
        assert r.status_code == 200
        row = r.json()["data"][0]
        assert row["date"] == "2026-01-05"
        assert row["open"] == 3411.0
        assert row["close"] == 3399.0
        assert row["volume"] == 18505900

    def test_404_on_empty(self):
        with patch("main.yf.Ticker", return_value=_mock_ticker([])):
            r = client.get("/api/stock/9999")
        assert r.status_code == 404

    def test_500_on_exception(self):
        m = MagicMock()
        m.history.side_effect = Exception("network error")
        with patch("main.yf.Ticker", return_value=m):
            r = client.get("/api/stock/7203")
        assert r.status_code == 500

    def test_result_sorted_by_date(self):
        rows = [
            {"date": "2026-01-06", "Open": 3488.0, "High": 3504.0, "Low": 3423.0, "Close": 3429.0, "Volume": 21996200},
            {"date": "2026-01-05", "Open": 3411.0, "High": 3455.0, "Low": 3397.0, "Close": 3399.0, "Volume": 18505900},
        ]
        with patch("main.yf.Ticker", return_value=_mock_ticker(rows)):
            r = client.get("/api/stock/7203")
        dates = [row["date"] for row in r.json()["data"]]
        assert dates == sorted(dates)

    def test_appends_T_suffix_to_ticker(self):
        with patch("main.yf.Ticker", return_value=_mock_ticker(SAMPLE_ROWS)) as mock_ticker:
            client.get("/api/stock/7203")
        mock_ticker.assert_called_once_with("7203.T")

    def test_accepts_from_to_params(self):
        with patch("main.yf.Ticker", return_value=_mock_ticker(SAMPLE_ROWS)) as mock_ticker:
            client.get("/api/stock/7203?from=20260101&to=20260201")
        mock_ticker.return_value.history.assert_called_once_with(
            start="2026-01-01", end="2026-02-01"
        )


class TestGetStockInfo:
    def test_returns_info(self):
        with patch("main.yf.Ticker", return_value=_mock_ticker([], SAMPLE_INFO)):
            r = client.get("/api/stock/7203/info")
        assert r.status_code == 200
        body = r.json()
        assert body["name"] == "Toyota Motor Corporation"
        assert body["sector"] == "Consumer Cyclical"

    def test_404_when_not_found(self):
        with patch("main.yf.Ticker", return_value=_mock_ticker([], {})):
            r = client.get("/api/stock/9999/info")
        assert r.status_code == 404

    def test_500_on_exception(self):
        m = MagicMock()
        type(m).info = PropertyMock(side_effect=Exception("error"))
        with patch("main.yf.Ticker", return_value=m):
            r = client.get("/api/stock/7203/info")
        assert r.status_code == 500


class TestCors:
    def test_allows_localhost(self):
        r = client.get("/api/stock/7203", headers={"Origin": "http://localhost:3000"})
        assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_blocks_unknown_origin(self):
        r = client.get("/api/stock/7203", headers={"Origin": "https://evil.example.com"})
        assert r.headers.get("access-control-allow-origin") != "https://evil.example.com"
