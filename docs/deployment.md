# デプロイ・インフラ仕様

## 構成概要

| 役割 | サービス | URL（例） |
|------|---------|---------|
| フロントエンド | Vercel | `https://stock-chart-app.vercel.app` |
| バックエンド | Render | `https://stock-chart-backend.onrender.com` |

---

## 環境変数

### バックエンド（`backend/.env`）

| 変数名 | 必須 | 説明 | 例 |
|--------|------|------|-----|
| `JQUANTS_API_KEY` | ✓ | J-Quants API キー | `bvxpwHTK4_...` |
| `ALLOWED_ORIGINS` | — | CORS 許可 origin（カンマ区切り）。未設定時は `http://localhost:3000` | `https://stock-chart-app.vercel.app` |

### フロントエンド（`frontend/.env.local`）

| 変数名 | 必須 | 説明 | 例 |
|--------|------|------|-----|
| `NEXT_PUBLIC_API_BASE_URL` | — | バックエンドの URL。未設定時は `http://localhost:8000` | `https://stock-chart-backend.onrender.com` |

> **注意**: `.env` / `.env.local` は `.gitignore` で除外済み。コミットしないこと。  
> テンプレートは `backend/.env.example` を参照。

---

## ローカル開発

### 前提条件

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)（Python パッケージマネージャ）
- Node.js 18+
- J-Quants API キー

### セットアップ手順

```bash
# 1. リポジトリをクローン
git clone https://github.com/zaqwedcxzasd/stock-chart-app.git
cd stock-chart-app

# 2. バックエンドの環境変数を設定
cp backend/.env.example backend/.env
# backend/.env を編集して JQUANTS_API_KEY を入力

# 3. バックエンドの依存パッケージをインストール
cd backend && uv sync && cd ..

# 4. フロントエンドの依存パッケージをインストール
cd frontend && npm install && cd ..
```

### 起動

```bash
# ターミナル 1: バックエンド
cd backend
uv run uvicorn main:app --reload
# → http://localhost:8000

# ターミナル 2: フロントエンド
cd frontend
npm run dev
# → http://localhost:3000
```

---

## Render（バックエンド）デプロイ手順

`render.yaml` をリポジトリに含めているため、Render が自動検出する。

### 初回設定

1. [Render ダッシュボード](https://dashboard.render.com) で **New → Web Service**
2. リポジトリを接続
3. 以下を確認（`render.yaml` から自動入力される）:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install uv && uv sync --no-dev`
   - **Start Command**: `uv run uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables** でシークレットを手動設定:
   - `JQUANTS_API_KEY` = J-Quants API キー
   - `ALLOWED_ORIGINS` = Vercel のデプロイ URL（`https://your-app.vercel.app`）
5. **Create Web Service**

### `render.yaml` の内容

```yaml
services:
  - type: web
    name: stock-chart-backend
    runtime: python
    rootDir: backend
    buildCommand: pip install uv && uv sync --no-dev
    startCommand: uv run uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: JQUANTS_API_KEY
        sync: false
      - key: ALLOWED_ORIGINS
        sync: false
```

`sync: false` は「Render ダッシュボードで手動設定する変数」を意味し、YAML に値を書かない。

---

## Vercel（フロントエンド）デプロイ手順

Next.js プロジェクトは Vercel が自動検出する。

### 初回設定

1. [Vercel ダッシュボード](https://vercel.com/dashboard) で **New Project**
2. リポジトリを接続
3. **Root Directory** を `frontend` に変更
4. **Environment Variables** を設定:
   - `NEXT_PUBLIC_API_BASE_URL` = Render のデプロイ URL（`https://stock-chart-backend.onrender.com`）
5. **Deploy**

### 注意事項

- `NEXT_PUBLIC_` プレフィックスが必要。これがないとブラウザ側のコードから参照できない。
- Vercel のプレビュー環境（PR ごとのデプロイ）では、`NEXT_PUBLIC_API_BASE_URL` が本番の Render URL を向くため CORS の問題は発生しない（Render の `ALLOWED_ORIGINS` にはプレビュー URL も追加が必要な場合あり）。

---

## デプロイ後の確認

```bash
# バックエンドの死活確認
curl https://stock-chart-backend.onrender.com/api/stock/7203?from=20260101&to=20260414

# フロントエンドの確認
# ブラウザで https://your-app.vercel.app を開き、7203 で検索
```

---

## テスト

```bash
# バックエンド（13件）
cd backend && uv run pytest -v

# フロントエンド（6件）
cd frontend && npm test
```

CI/CD パイプラインは未設定（現状は手動でテストを実行してからマージする）。
