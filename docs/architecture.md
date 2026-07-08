# システムアーキテクチャ

## 概要

日本株の銘柄コードを入力すると、Yahoo Finance から日足株価データを取得してチャート表示する Web アプリ。

## 技術スタック

| レイヤー | 技術 | バージョン |
|---------|------|----------|
| フロントエンド | Next.js (App Router) | 16.x |
| フロントエンド | TypeScript | 5.x |
| フロントエンド | Tailwind CSS | v4 |
| フロントエンド | Recharts | 3.x |
| バックエンド | FastAPI | 0.138.x |
| バックエンド | Python | 3.12 |
| バックエンド | uv（パッケージ管理） | 最新 |
| データソース | Yahoo Finance (yfinance) | 1.x |

## システム構成

```
ブラウザ
  │
  │  HTTP (localhost:3000 / Vercel)
  ▼
┌─────────────────────────┐
│   Next.js フロントエンド  │
│   - StockViewer         │  ← 検索・期間選択・状態管理
│   - StockChart          │  ← Recharts によるチャート描画
└───────────┬─────────────┘
            │ HTTP (localhost:8000 / Render)
            │ GET /api/stock/{code}
            │ GET /api/stock/{code}/info
            ▼
┌─────────────────────────┐
│   FastAPI バックエンド    │
│   - CORS ミドルウェア    │
│   - 株価エンドポイント    │
│   - 銘柄情報エンドポイント│
└───────────┬─────────────┘
            │ HTTPS
            ▼
┌─────────────────────────┐
│   Yahoo Finance          │
│   - yfinance ライブラリ  │  ← 日足 OHLCV・銘柄情報
└─────────────────────────┘
```

## データフロー

1. ユーザーが銘柄コード（例: `7203`）と期間（1M / 3M / 1Y）を入力して検索
2. フロントエンドがバックエンドの `/api/stock/{code}?from=...&to=...` を呼び出す
3. バックエンドが yfinance 経由で Yahoo Finance からデータを取得する
4. yfinance が日足データを pandas DataFrame で返す
5. バックエンドが日付昇順に並べてフロントエンドへ返す
6. フロントエンドが終値ラインチャート＋出来高バーチャートを描画する

銘柄情報（社名・業種・市場）は `/api/stock/{code}/info` から並行して取得し、チャートのヘッダーに表示する。

## ディレクトリ構成

```
stock-app/
├── backend/
│   ├── main.py              # FastAPI アプリ本体
│   ├── tests/
│   │   └── test_main.py     # pytest テスト（11件）
│   ├── pyproject.toml       # 依存パッケージ定義
│   ├── .env                 # 環境変数（gitignore済み）
│   └── .env.example         # 環境変数テンプレート
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx   # ルートレイアウト
│   │   │   └── page.tsx     # トップページ
│   │   ├── components/
│   │   │   ├── StockViewer.tsx  # 検索・状態管理
│   │   │   └── StockChart.tsx   # チャート描画
│   │   ├── lib/
│   │   │   └── api.ts       # バックエンド API クライアント
│   │   └── test/
│   │       └── StockViewer.test.tsx  # Vitest テスト（6件）
│   └── .env.local           # 環境変数（gitignore済み）
├── docs/                    # 本仕様書群
├── render.yaml              # Render デプロイ設定
└── README.md                # プロジェクト概要・起動方法
```
