"use client";

import { useState, useCallback } from "react";
import { fetchStockPrices, fetchStockInfo, type DailyBar, type StockInfo, type Period } from "@/lib/api";
import StockChart from "./StockChart";

const PERIODS: { label: string; value: Period }[] = [
  { label: "1ヶ月", value: "1M" },
  { label: "3ヶ月", value: "3M" },
  { label: "1年", value: "1Y" },
];

export default function StockViewer() {
  const [inputCode, setInputCode] = useState("");
  const [period, setPeriod] = useState<Period>("1Y");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<DailyBar[] | null>(null);
  const [info, setInfo] = useState<StockInfo | null>(null);
  const [lastCode, setLastCode] = useState("");

  const search = useCallback(async (code: string, p: Period) => {
    const trimmed = code.trim();
    if (!trimmed) return;
    setLoading(true);
    setError(null);
    try {
      const [prices, stockInfo] = await Promise.allSettled([
        fetchStockPrices(trimmed, p),
        fetchStockInfo(trimmed),
      ]);
      if (prices.status === "rejected") throw new Error(prices.reason?.message ?? "データ取得に失敗しました");
      setData(prices.value.data);
      setInfo(stockInfo.status === "fulfilled" ? stockInfo.value : null);
      setLastCode(trimmed);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "予期しないエラーが発生しました");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSubmit = (e: React.FormEvent) => { e.preventDefault(); search(inputCode, period); };
  const handlePeriod = (p: Period) => { setPeriod(p); if (lastCode) search(lastCode, p); };

  const latestClose = data?.at(-1)?.close;
  const prevClose = data && data.length > 1 ? data[data.length - 2].close : null;
  const change = latestClose != null && prevClose != null
    ? ((latestClose - prevClose) / prevClose) * 100 : null;

  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight text-slate-100">日本株チャート</h1>
        <p className="mt-1 text-sm text-slate-500">銘柄コードを入力して株価チャートを表示</p>
      </div>

      <form onSubmit={handleSubmit} className="mb-6 flex gap-2">
        <input
          type="text" value={inputCode} onChange={(e) => setInputCode(e.target.value)}
          placeholder="銘柄コード（例: 7203）" maxLength={5}
          className="h-10 flex-1 rounded-lg border border-slate-700 bg-slate-800 px-4 text-sm text-slate-100 placeholder-slate-500 outline-none transition focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
        />
        <button type="submit" disabled={loading || !inputCode.trim()}
          className="h-10 rounded-lg bg-sky-500 px-5 text-sm font-medium text-white transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-50">
          {loading ? "取得中…" : "検索"}
        </button>
      </form>

      {data && (
        <div className="mb-6 flex gap-1">
          {PERIODS.map(({ label, value }) => (
            <button key={value} onClick={() => handlePeriod(value)} disabled={loading}
              className={`rounded-md px-4 py-1.5 text-sm font-medium transition ${period === value ? "bg-sky-500 text-white" : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"}`}>
              {label}
            </button>
          ))}
        </div>
      )}

      {loading && (
        <div className="flex h-64 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-700 border-t-sky-500" />
        </div>
      )}

      {!loading && error && (
        <div className="rounded-lg border border-red-800 bg-red-950/40 px-4 py-3 text-sm text-red-400">{error}</div>
      )}

      {!loading && data && (
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4 sm:p-6">
          {latestClose != null && (
            <div className="mb-4 flex items-baseline gap-3">
              <span className="text-3xl font-semibold tabular-nums text-slate-100">
                ¥{latestClose.toLocaleString("ja-JP")}
              </span>
              {change != null && (
                <span className={`text-sm font-medium ${change >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                  {change >= 0 ? "+" : ""}{change.toFixed(2)}%
                </span>
              )}
            </div>
          )}
          <StockChart data={data} info={info} />
        </div>
      )}

      {!loading && !error && !data && (
        <div className="flex h-64 flex-col items-center justify-center text-slate-600">
          <svg className="mb-3 h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
          </svg>
          <p className="text-sm">銘柄コードを入力して検索してください</p>
        </div>
      )}
    </div>
  );
}
