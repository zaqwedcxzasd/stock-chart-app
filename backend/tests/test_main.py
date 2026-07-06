import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from main import app

client = TestClient(app)

MOCK_PRICES = {
    "data": [
        {"Date": "2024-01-05", "Code": "72030", "O": 2500.0, "H": 2600.0,
         "L": 2480.0, "C": 2550.0, "Vo": 10000000.0},
    ]
}

MOCK_INFO = {
    "data": [
        {"Code": "72030", "CoName": "トヨタ自動車", "CoNameEn": "Toyota Motor Corporation",
         "S33Nm": "輸送用機器", "MktNm": "プライム"},
    ]
}


def _resp(body: dict, status: int = 200) -> Response:
    return Response(status_code=status, content=json.dumps(body).encode())


class TestGetStockPrices:
    def test_returns_ohlcv(self):
        with patch("main.os.getenv", return_value="dummy"), \
             patch("httpx.AsyncClient.get", new_callable=AsyncMock) as m:
            m.return_value = _resp(MOCK_PRICES)
            r = client.get("/api/stock/7203")
        assert r.status_code == 200
        row = r.json()["data"][0]
        assert row == {"date": "2024-01-05", "open": 2500.0, "high": 2600.0,
                       "low": 2480.0, "close": 2550.0, "volume": 10000000.0}

    def test_404_on_empty(self):
        with patch("main.os.getenv", return_value="dummy"), \
             patch("httpx.AsyncClient.get", new_callable=AsyncMock) as m:
            m.return_value = _resp({"data": []})
            r = client.get("/api/stock/9999")
        assert r.status_code == 404

    def test_400_subscription_error(self):
        msg = "Your subscription covers the following dates: 2024-04-14 ~ 2026-04-14."
        with patch("main.os.getenv", return_value="dummy"), \
             patch("httpx.AsyncClient.get", new_callable=AsyncMock) as m:
            m.return_value = _resp({"message": msg}, status=400)
            r = client.get("/api/stock/7203")
        assert r.status_code == 400
        assert "subscription" in r.json()["detail"]

    def test_401_on_auth_error(self):
        with patch("main.os.getenv", return_value="bad"), \
             patch("httpx.AsyncClient.get", new_callable=AsyncMock) as m:
            m.return_value = _resp({}, status=401)
            r = client.get("/api/stock/7203")
        assert r.status_code == 401

    def test_429_on_rate_limit(self):
        with patch("main.os.getenv", return_value="dummy"), \
             patch("httpx.AsyncClient.get", new_callable=AsyncMock) as m:
            m.return_value = _resp({}, status=429)
            r = client.get("/api/stock/7203")
        assert r.status_code == 429

    def test_500_when_no_api_key(self):
        with patch("main.os.getenv", return_value=None):
            r = client.get("/api/stock/7203")
        assert r.status_code == 500

    def test_pagination(self):
        p1 = {"data": [{"Date": "2024-01-04", "Code": "72030", "O": 2400.0,
                         "H": 2450.0, "L": 2390.0, "C": 2420.0, "Vo": 9000000.0}],
              "pagination_key": "next"}
        p2 = {"data": [{"Date": "2024-01-05", "Code": "72030", "O": 2500.0,
                         "H": 2600.0, "L": 2480.0, "C": 2550.0, "Vo": 10000000.0}]}
        with patch("main.os.getenv", return_value="dummy"), \
             patch("httpx.AsyncClient.get", new_callable=AsyncMock) as m:
            m.side_effect = [_resp(p1), _resp(p2)]
            r = client.get("/api/stock/7203")
        assert r.status_code == 200
        assert len(r.json()["data"]) == 2

    def test_result_sorted_by_date(self):
        unsorted = {
            "data": [
                {"Date": "2024-01-05", "Code": "72030", "O": 2500.0, "H": 2600.0,
                 "L": 2480.0, "C": 2550.0, "Vo": 10000000.0},
                {"Date": "2024-01-03", "Code": "72030", "O": 2300.0, "H": 2400.0,
                 "L": 2280.0, "C": 2350.0, "Vo": 8000000.0},
            ]
        }
        with patch("main.os.getenv", return_value="dummy"), \
             patch("httpx.AsyncClient.get", new_callable=AsyncMock) as m:
            m.return_value = _resp(unsorted)
            r = client.get("/api/stock/7203")
        dates = [row["date"] for row in r.json()["data"]]
        assert dates == sorted(dates)


class TestGetStockInfo:
    def test_returns_info(self):
        with patch("main.os.getenv", return_value="dummy"), \
             patch("httpx.AsyncClient.get", new_callable=AsyncMock) as m:
            m.return_value = _resp(MOCK_INFO)
            r = client.get("/api/stock/7203/info")
        assert r.status_code == 200
        body = r.json()
        assert body["name"] == "トヨタ自動車"
        assert body["name_english"] == "Toyota Motor Corporation"
        assert body["sector"] == "輸送用機器"
        assert body["market"] == "プライム"

    def test_404_when_not_found(self):
        with patch("main.os.getenv", return_value="dummy"), \
             patch("httpx.AsyncClient.get", new_callable=AsyncMock) as m:
            m.return_value = _resp({"data": []})
            r = client.get("/api/stock/9999/info")
        assert r.status_code == 404

    def test_401_on_auth_error(self):
        with patch("main.os.getenv", return_value="bad"), \
             patch("httpx.AsyncClient.get", new_callable=AsyncMock) as m:
            m.return_value = _resp({}, status=401)
            r = client.get("/api/stock/7203/info")
        assert r.status_code == 401


class TestCors:
    def test_allows_localhost(self):
        r = client.get(
            "/api/stock/7203",
            headers={"Origin": "http://localhost:3000"},
        )
        assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_blocks_unknown_origin(self):
        r = client.get(
            "/api/stock/7203",
            headers={"Origin": "https://evil.example.com"},
        )
        assert r.headers.get("access-control-allow-origin") != "https://evil.example.com"
