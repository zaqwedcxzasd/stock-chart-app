# 日本株チャートビューア

銘柄コードを入力すると日足の株価チャート（終値ライン＋出来高）を表示する Web アプリ。

## 技術スタック

| 役割 | 技術 |
|------|------|
| バックエンド | FastAPI (Python) / uv |
| フロントエンド | Next.js 16 / TypeScript / Tailwind CSS v4 |
| チャート | Recharts |
| データソース | J-Quants API v2 |

## 前提条件

- Python 3.12+、[uv](https://docs.astral.sh/uv/) がインストール済み
- Node.js 18+ がインストール済み
- J-Quants API キー（[jpx-jquants.com](https://jpx-jquants.com) で取得）

## セットアップ

```bash
# 1. リポジトリをクローン
git clone https://github.com/zaqwedcxzasd/stock-chart-app.git
cd stock-chart-app

# 2. APIキーを設定
echo 'JQUANTS_API_KEY=your_api_key_here' > backend/.env

# 3. バックエンドの依存パッケージをインストール
cd backend && uv sync && cd ..

# 4. フロントエンドの依存パッケージをインストール
cd frontend && npm install && cd ..
```

## 起動方法

ターミナルを2つ開いて、それぞれで実行する。

**バックエンド（ポート 8000）**

```bash
cd backend
uv run uvicorn main:app --reload
```

**フロントエンド（ポート 3000）**

```bash
cd frontend
npm run dev
```

ブラウザで `http://localhost:3000` を開き、銘柄コード（例: `7203`）を入力して検索。

## API エンドポイント

| メソッド | パス | 説明 |
|----------|------|------|
| GET | `/api/stock/{code}` | 日足 OHLCV（四本値＋出来高）を返す |
| GET | `/api/stock/{code}/info` | 銘柄名・業種・市場を返す |

クエリパラメータ `from` / `to`（形式: `YYYYMMDD`）で取得期間を指定できる。省略時は直近1年。

## テスト

```bash
# バックエンド
cd backend && uv run pytest

# フロントエンド
cd frontend && npm test
```

## 注意事項

- `backend/.env` は `.gitignore` で除外済み。絶対にコミットしないこと。
- J-Quants のプランによって取得できる日付範囲が異なる。範囲外を指定するとエラーが返る。
