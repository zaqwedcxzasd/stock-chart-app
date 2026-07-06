import os
from datetime import date, timedelta
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI(title="Stock Chart API")

_allowed_origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

JQUANTS_BASE_URL = "https://api.jquants.com/v2"


def _api_key() -> str:
    key = os.getenv("JQUANTS_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="JQUANTS_API_KEY is not configured")
    return key


def _raise_for_jquants_error(resp: httpx.Response) -> None:
    if resp.status_code == 200:
        return
    if resp.status_code == 400:
        try:
            msg = resp.json().get("message", resp.text)
        except Exception:
            msg = resp.text
        raise HTTPException(status_code=400, detail=msg)
    messages = {
        401: "J-Quants API authentication failed (invalid API key)",
        403: "J-Quants API access denied (check your plan)",
        429: "J-Quants API rate limit exceeded — please retry later",
    }
    detail = messages.get(resp.status_code, f"J-Quants API error {resp.status_code}: {resp.text}")
    raise HTTPException(status_code=resp.status_code, detail=detail)


@app.get("/api/stock/{code}")
async def get_stock_prices(
    code: str,
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
):
    today = date.today()
    if not from_date:
        from_date = (today - timedelta(days=365)).strftime("%Y%m%d")
    if not to_date:
        to_date = today.strftime("%Y%m%d")

    headers = {"x-api-key": _api_key()}
    all_rows: list[dict] = []
    pagination_key: Optional[str] = None

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            params: dict = {"code": code, "from": from_date, "to": to_date}
            if pagination_key:
                params["pagination_key"] = pagination_key

            resp = await client.get(
                f"{JQUANTS_BASE_URL}/equities/bars/daily",
                params=params,
                headers=headers,
            )
            _raise_for_jquants_error(resp)

            body = resp.json()
            all_rows.extend(body.get("data", []))
            pagination_key = body.get("pagination_key")
            if not pagination_key:
                break

    if not all_rows:
        raise HTTPException(status_code=404, detail=f"No price data found for code '{code}'")

    result = [
        {
            "date": row["Date"],
            "open": row.get("O"),
            "high": row.get("H"),
            "low": row.get("L"),
            "close": row.get("C"),
            "volume": row.get("Vo"),
        }
        for row in all_rows
    ]
    result.sort(key=lambda x: x["date"])

    return {"code": code, "data": result}


@app.get("/api/stock/{code}/info")
async def get_stock_info(code: str):
    headers = {"x-api-key": _api_key()}

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"{JQUANTS_BASE_URL}/equities/master",
            params={"code": code},
            headers=headers,
        )
        _raise_for_jquants_error(resp)

    items = resp.json().get("data", [])
    if not items:
        raise HTTPException(status_code=404, detail=f"Stock info not found for code '{code}'")

    item = items[-1]
    return {
        "code": item.get("Code"),
        "name": item.get("CoName"),
        "name_english": item.get("CoNameEn"),
        "sector": item.get("S33Nm"),
        "market": item.get("MktNm"),
    }
