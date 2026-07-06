const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

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

function fmt(d: Date): string {
  return d.toISOString().slice(0, 10).replace(/-/g, "");
}

function periodToDates(period: Period): { from: string; to: string } {
  const to = new Date();
  const from = new Date(to);
  if (period === "1M") from.setMonth(from.getMonth() - 1);
  else if (period === "3M") from.setMonth(from.getMonth() - 3);
  else from.setFullYear(from.getFullYear() - 1);
  return { from: fmt(from), to: fmt(to) };
}

export async function fetchStockPrices(
  code: string,
  period: Period,
): Promise<StockPricesResponse> {
  const { from, to } = periodToDates(period);
  const res = await fetch(`${API_BASE}/api/stock/${code}?from=${from}&to=${to}`);
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
