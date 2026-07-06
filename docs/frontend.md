# フロントエンド仕様

## 画面構成

アプリはトップページ 1 画面のみ。URL ルーティングは存在しない。

```
┌─────────────────────────────────────────┐
│  日本株チャート                           │
│  銘柄コードを入力して株価チャートを表示      │
│                                         │
│  ┌──────────────────────┐ ┌────────┐   │
│  │ 銘柄コード（例: 7203）  │ │  検索  │   │
│  └──────────────────────┘ └────────┘   │
│                                         │
│  [ 1ヶ月 ] [ 3ヶ月 ] [ 1年 ]            │  ← 検索後に表示
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ トヨタ自動車  7203               │   │
│  │ 輸送用機器 · プライム            │   │
│  │                                 │   │
│  │  ¥3,399  +1.23%                │   │
│  │                                 │   │
│  │  [終値ラインチャート]             │   │
│  │                                 │   │
│  │  [出来高バーチャート]             │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 状態一覧

| 状態 | 表示内容 |
|------|---------|
| 初期（未検索） | 「銘柄コードを入力して検索してください」のプレースホルダー |
| ローディング中 | スピナー（検索ボタンは「取得中…」で無効化） |
| 取得成功 | 期間ボタン＋株価チャートカード |
| エラー | 赤背景のエラーメッセージ |

---

## コンポーネント構成

```
page.tsx
└── StockViewer            ← Client Component（状態管理・API呼び出し）
    └── StockChart         ← Client Component（チャート描画）
```

### StockViewer

`src/components/StockViewer.tsx`

画面全体の状態を管理するルートコンポーネント。

**状態（useState）**

| 状態変数 | 型 | 説明 |
|---------|-----|------|
| `inputCode` | string | 入力欄の銘柄コード |
| `lastCode` | string | 最後に検索した銘柄コード |
| `period` | `"1M" \| "3M" \| "1Y"` | 選択中の期間 |
| `loading` | boolean | API 取得中フラグ |
| `error` | string \| null | エラーメッセージ |
| `data` | DailyBar[] \| null | 取得した日足データ |
| `info` | StockInfo \| null | 取得した銘柄情報 |

**動作**

- フォーム送信時: `/api/stock/{code}` と `/api/stock/{code}/info` を `Promise.allSettled` で並行取得
- 銘柄情報の取得失敗は非致命的（チャートは表示し、ヘッダー情報を省略）
- 期間ボタン押下時: `lastCode` で再検索

### StockChart

`src/components/StockChart.tsx`

Recharts を使って 2 段構成のチャートを描画する。

**Props**

| Prop | 型 | 説明 |
|------|----|------|
| `data` | DailyBar[] | 日足データの配列 |
| `info` | StockInfo \| null | 銘柄情報（null の場合ヘッダーを非表示） |

**チャート構成**

| 段 | 種類 | 高さ | データ |
|----|------|------|--------|
| 上段 | ラインチャート（ComposedChart + Line） | 256px（sm: 320px） | 終値（close） |
| 下段 | バーチャート（ComposedChart + Bar） | 96px | 出来高（volume） |

- Y 軸の範囲は最小値・最大値に 5% のパディングを付けて自動計算
- カスタム Tooltip で終値（`¥` 付き）と出来高（`K` / `M` 単位）を表示

---

## API クライアント

`src/lib/api.ts`

バックエンドへの fetch を集約したモジュール。

**エクスポートする関数**

| 関数 | 説明 |
|------|------|
| `fetchStockPrices(code, period)` | 日足 OHLCV を取得 |
| `fetchStockInfo(code)` | 銘柄情報を取得 |

**エクスポートする型**

| 型 | 説明 |
|----|------|
| `DailyBar` | 1日分の OHLCV |
| `StockPricesResponse` | `/api/stock/{code}` のレスポンス |
| `StockInfo` | `/api/stock/{code}/info` のレスポンス |
| `Period` | `"1M" \| "3M" \| "1Y"` |

バックエンドの URL は `NEXT_PUBLIC_API_BASE_URL` 環境変数で指定する。未設定時は `http://localhost:8000`。

---

## デザイン

| 項目 | 値 |
|------|----|
| 背景 | `slate-950`（ダークテーマ固定） |
| カード背景 | `slate-900` |
| ボーダー | `slate-800` |
| テキスト（主） | `slate-100` |
| テキスト（副） | `slate-400` / `slate-500` |
| アクセント | `sky-500`（ボタン・ラインチャート） |
| 上昇 | `emerald-400` |
| 下落 | `red-400` |

---

## テスト

`src/test/StockViewer.test.tsx`（Vitest + Testing Library、6件）

| テスト | 内容 |
|--------|------|
| renders search input and button | 検索フォームが描画される |
| shows empty state initially | 初期表示にプレースホルダーが出る |
| disables search button when input is empty | 入力なしはボタンが無効 |
| displays stock data after search | 検索成功時に社名・株価が表示される |
| shows error on API failure | API エラー時にエラーメッセージが出る |
| shows period selector after successful search | 検索成功後に期間ボタンが出る |

Recharts は jsdom 環境で動作しないため、テスト内でモック化している。
