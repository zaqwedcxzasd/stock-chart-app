# 日本株チャートビューア

銘柄コードを入力すると日足の株価チャート（終値ライン＋出来高）を表示する Web アプリ。

## 技術スタック

| 役割 | 技術 | ホスティング |
|------|------|------------|
| バックエンド | FastAPI (Python) / uv | Render |
| フロントエンド | Next.js 16 / TypeScript / Tailwind CSS v4 | Vercel |
| チャート | Recharts | — |
| データソース | J-Quants API v2 | — |

## ローカル開発

### 前提条件

- Python 3.12+、[uv](https://docs.astral.sh/uv/) がインストール済み
- Node.js 18+ がインストール済み
- J-Quants API キー（[jpx-jquants.com](https://jpx-jquants.com) で取得）

### セットアップ

```bash
git clone https://github.com/zaqwedcxzasd/stock-chart-app.git
cd stock-chart-app

# バックエンドの環境変数
cp backend/.env.example backend/.env
# backend/.env を編集して JQUANTS_API_KEY を設定

# バックエンドの依存パッケージ
cd backend && uv sync && cd ..

# フロントエンドの依存パッケージ
cd frontend && npm install && cd ..
```

### 起動

ターミナルを 2 つ開いて、それぞれで実行する。

```bash
# ターミナル 1: バックエンド（ポート 8000）
cd backend
uv run uvicorn main:app --reload

# ターミナル 2: フロントエンド（ポート 3000）
cd frontend
npm run dev
```

ブラウザで `http://localhost:3000` を開き、銘柄コード（例: `7203`）を入力して検索。

## テスト

```bash
# バックエンド（11 件）
cd backend && uv run pytest -v

# フロントエンド（6 件）
cd frontend && npm test
```

## デプロイ

### バックエンド（Render）

1. Render ダッシュボードで「New Web Service」→ このリポジトリを選択
2. Root Directory: `backend`
3. Build Command: `pip install uv && uv sync --no-dev`
4. Start Command: `uv run uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Environment Variables を設定:
   - `JQUANTS_API_KEY` = J-Quants API キー
   - `ALLOWED_ORIGINS` = Vercel のデプロイ URL（例: `https://your-app.vercel.app`）

`render.yaml` をリポジトリに含めているので、Render が自動で検出します。

### フロントエンド（Vercel）

1. Vercel ダッシュボードで「New Project」→ このリポジトリを選択
2. Root Directory: `frontend`
3. Environment Variables を設定:
   - `NEXT_PUBLIC_API_BASE_URL` = Render のデプロイ URL（例: `https://stock-chart-backend.onrender.com`）

## API エンドポイント

| メソッド | パス | 説明 |
|----------|------|------|
| GET | `/api/stock/{code}` | 日足 OHLCV（四本値＋出来高） |
| GET | `/api/stock/{code}/info` | 銘柄名・業種・市場 |

クエリパラメータ `from` / `to`（形式: `YYYYMMDD`）で期間指定可。省略時は直近1年。

## 環境変数一覧

| ファイル | 変数名 | 説明 |
|----------|--------|------|
| `backend/.env` | `JQUANTS_API_KEY` | J-Quants API キー（必須） |
| `backend/.env` | `ALLOWED_ORIGINS` | CORS 許可 origin（カンマ区切り、省略時は `http://localhost:3000`） |
| `frontend/.env.local` | `NEXT_PUBLIC_API_BASE_URL` | バックエンド URL（省略時は `http://localhost:8000`） |

> **注意**: `.env` / `.env.local` は `.gitignore` で除外済み。絶対にコミットしないこと。
> テンプレートは `backend/.env.example` を参照。
