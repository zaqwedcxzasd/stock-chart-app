import os
from datetime import date, timedelta
from typing import Optional

import yfinance as yf
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


def _ticker(code: str) -> str:
    return f"{code}.T"


@app.get("/api/stock/{code}")
async def get_stock_prices(
    code: str,
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
):
    today = date.today()
    start = from_date or (today - timedelta(days=365)).strftime("%Y%m%d")
    end = to_date or today.strftime("%Y%m%d")

    # YYYYMMDD → YYYY-MM-DD
    start_str = f"{start[:4]}-{start[4:6]}-{start[6:]}"
    end_str = f"{end[:4]}-{end[4:6]}-{end[6:]}"

    try:
        ticker = yf.Ticker(_ticker(code))
        hist = ticker.history(start=start_str, end=end_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データ取得エラー: {e}")

    if hist.empty:
        raise HTTPException(status_code=404, detail=f"No price data found for code '{code}'")

    result = [
        {
            "date": idx.strftime("%Y-%m-%d"),
            "open": round(row["Open"], 2) if row["Open"] else None,
            "high": round(row["High"], 2) if row["High"] else None,
            "low": round(row["Low"], 2) if row["Low"] else None,
            "close": round(row["Close"], 2) if row["Close"] else None,
            "volume": int(row["Volume"]) if row["Volume"] else None,
        }
        for idx, row in hist.iterrows()
    ]

    result.sort(key=lambda x: x["date"])
    return {"code": code, "data": result}


@app.get("/api/stock/{code}/info")
async def get_stock_info(code: str):
    try:
        ticker = yf.Ticker(_ticker(code))
        info = ticker.info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"情報取得エラー: {e}")

    if not info or info.get("quoteType") is None:
        raise HTTPException(status_code=404, detail=f"Stock info not found for code '{code}'")

    return {
        "code": code,
        "name": info.get("longName") or info.get("shortName"),
        "name_english": info.get("longName"),
        "sector": info.get("sector"),
        "market": info.get("exchange"),
    }
