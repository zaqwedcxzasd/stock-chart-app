const API_BASE = "http://localhost:8000";

export interface DailyBar {
  date: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
}

export interface StockPricesResponse {
  code: string;
  data: DailyBar[];
}

export interface StockInfo {
  code: string;
  name: string;
  name_english: string;
  sector: string;
  market: string;
}

export type Period = "1M" | "3M" | "1Y";

function periodToFromDate(period: Period): string {
  const d = new Date();
  if (period === "1M") d.setMonth(d.getMonth() - 1);
  else if (period === "3M") d.setMonth(d.getMonth() - 3);
  else d.setFullYear(d.getFullYear() - 1);
  return d.toISOString().slice(0, 10).replace(/-/g, "");
}

export async function fetchStockPrices(
  code: string,
  period: Period,
): Promise<StockPricesResponse> {
  const from = periodToFromDate(period);
  const res = await fetch(`${API_BASE}/api/stock/${code}?from=${from}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchStockInfo(code: string): Promise<StockInfo> {
  const res = await fetch(`${API_BASE}/api/stock/${code}/info`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}
