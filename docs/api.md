# API 仕様

バックエンドが提供する REST API の仕様。  
ローカル開発時のベース URL: `http://localhost:8000`

FastAPI の自動生成ドキュメントは起動後に `http://localhost:8000/docs` で参照できる。

---

## GET /api/stock/{code}

指定銘柄の日足株価（OHLCV）を返す。

### リクエスト

| 項目 | 内容 |
|------|------|
| メソッド | GET |
| パス | `/api/stock/{code}` |

**パスパラメータ**

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `code` | string | ✓ | 銘柄コード（例: `7203`） |

**クエリパラメータ**

| パラメータ | 型 | 必須 | 説明 | デフォルト |
|-----------|-----|------|------|-----------|
| `from` | string | — | 取得開始日（`YYYYMMDD`） | 1年前 |
| `to` | string | — | 取得終了日（`YYYYMMDD`） | 今日 |

### レスポンス

**200 OK**

```json
{
  "code": "7203",
  "data": [
    {
      "date": "2026-01-05",
      "open": 3411.0,
      "high": 3455.0,
      "low": 3397.0,
      "close": 3399.0,
      "volume": 18505900.0
    }
  ]
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `code` | string | 銘柄コード |
| `data` | array | 日足データの配列（日付昇順） |
| `data[].date` | string | 日付（`YYYY-MM-DD`） |
| `data[].open` | number \| null | 始値 |
| `data[].high` | number \| null | 高値 |
| `data[].low` | number \| null | 安値 |
| `data[].close` | number \| null | 終値 |
| `data[].volume` | number \| null | 出来高 |

### エラーレスポンス

| ステータス | 原因 | `detail` の例 |
|-----------|------|--------------|
| 400 | J-Quants のサブスクリプション期間外 | `"Your subscription covers the following dates: ..."` |
| 401 | APIキー不正 | `"J-Quants API authentication failed (invalid API key)"` |
| 403 | プランによるアクセス拒否 | `"J-Quants API access denied (check your plan)"` |
| 404 | 該当銘柄のデータなし | `"No price data found for code '9999'"` |
| 429 | レート制限 | `"J-Quants API rate limit exceeded — please retry later"` |
| 500 | APIキー未設定 | `"JQUANTS_API_KEY is not configured"` |

---

## GET /api/stock/{code}/info

指定銘柄の基本情報（社名・業種・市場）を返す。

### リクエスト

| 項目 | 内容 |
|------|------|
| メソッド | GET |
| パス | `/api/stock/{code}/info` |

**パスパラメータ**

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `code` | string | ✓ | 銘柄コード（例: `7203`） |

### レスポンス

**200 OK**

```json
{
  "code": "72030",
  "name": "トヨタ自動車",
  "name_english": "TOYOTA MOTOR CORPORATION",
  "sector": "輸送用機器",
  "market": "プライム"
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `code` | string | 銘柄コード（5桁） |
| `name` | string | 社名（日本語） |
| `name_english` | string | 社名（英語） |
| `sector` | string | 33業種区分名 |
| `market` | string | 市場区分名（プライム / スタンダード / グロース） |

### エラーレスポンス

| ステータス | 原因 |
|-----------|------|
| 401 | APIキー不正 |
| 404 | 銘柄が存在しない |
| 500 | APIキー未設定 |

---

## CORS

`ALLOWED_ORIGINS` 環境変数で許可する origin を制御する（カンマ区切りで複数指定可）。  
未設定時のデフォルトは `http://localhost:3000`。

---

## J-Quants API との対応

| このAPIのエンドポイント | J-Quants API エンドポイント |
|----------------------|--------------------------|
| `GET /api/stock/{code}` | `GET /v2/equities/bars/daily` |
| `GET /api/stock/{code}/info` | `GET /v2/equities/master` |

J-Quants API へのリクエストには `x-api-key` ヘッダーで認証する。  
ページネーションは `pagination_key` を使って自動的に全件取得する。
