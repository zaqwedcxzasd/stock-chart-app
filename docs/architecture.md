# システムアーキテクチャ

## 概要

日本株の銘柄コードを入力すると、J-Quants API から日足株価データを取得してチャート表示する Web アプリ。

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
| データソース | J-Quants API | v2 |

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
            │ x-api-key ヘッダー認証
            ▼
┌─────────────────────────┐
│   J-Quants API v2        │
│   - /equities/bars/daily │  ← 日足 OHLCV
│   - /equities/master     │  ← 銘柄マスタ
└─────────────────────────┘
```

## データフロー

1. ユーザーが銘柄コード（例: `7203`）と期間（1M / 3M / 1Y）を入力して検索
2. フロントエンドがバックエンドの `/api/stock/{code}?from=...&to=...` を呼び出す
3. バックエンドが `x-api-key` ヘッダー付きで J-Quants API を呼び出す
4. J-Quants API がページネーション付きで日足データを返す
5. バックエンドが全ページを収集し、日付昇順に並べてフロントエンドへ返す
6. フロントエンドが終値ラインチャート＋出来高バーチャートを描画する

銘柄情報（社名・業種・市場）は `/api/stock/{code}/info` から並行して取得し、チャートのヘッダーに表示する。

## ディレクトリ構成

```
stock-app/
├── backend/
│   ├── main.py              # FastAPI アプリ本体
│   ├── tests/
│   │   └── test_main.py     # pytest テスト（13件）
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
