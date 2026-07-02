"use client";

import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { DailyBar, StockInfo } from "@/lib/api";

interface Props {
  data: DailyBar[];
  info: StockInfo | null;
}

function fmtDate(s: string) { return s.slice(5); }
function fmtVol(v: number) {
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `${(v / 1_000).toFixed(0)}K`;
  return String(v);
}
function fmtPrice(v: number) { return v.toLocaleString("ja-JP"); }

interface TooltipItem { value: number | null; name: string }
interface TooltipProps { active?: boolean; payload?: TooltipItem[]; label?: string }

function CustomTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload?.length) return null;
  const close = payload.find((p) => p.name === "終値");
  const vol = payload.find((p) => p.name === "出来高");
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm shadow-xl">
      <p className="mb-1 font-medium text-slate-300">{label}</p>
      {close?.value != null && <p className="text-sky-400">終値: ¥{fmtPrice(close.value)}</p>}
      {vol?.value != null && <p className="text-slate-500">出来高: {fmtVol(vol.value)}</p>}
    </div>
  );
}

export default function StockChart({ data, info }: Props) {
  const closes = data.map((d) => d.close).filter((v): v is number => v != null);
  const min = Math.min(...closes);
  const max = Math.max(...closes);
  const pad = (max - min) * 0.05 || 10;

  return (
    <div className="w-full">
      {info && (
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-slate-100">
            {info.name}
            <span className="ml-2 text-sm font-normal text-slate-400">{info.code}</span>
          </h2>
          <p className="text-sm text-slate-500">{info.sector} · {info.market}</p>
        </div>
      )}

      <div className="h-64 w-full sm:h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 8, right: 12, left: 8, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="date" tickFormatter={fmtDate} tick={{ fill: "#64748b", fontSize: 11 }}
              tickLine={false} axisLine={false} interval="preserveStartEnd" />
            <YAxis domain={[min - pad, max + pad]} tickFormatter={fmtPrice}
              tick={{ fill: "#64748b", fontSize: 11 }} tickLine={false} axisLine={false} width={70} />
            <Tooltip content={<CustomTooltip />} />
            <Line type="monotone" dataKey="close" name="終値" stroke="#38bdf8"
              dot={false} strokeWidth={1.5} connectNulls />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-2 h-24 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 0, right: 12, left: 8, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="date" hide />
            <YAxis tickFormatter={fmtVol} tick={{ fill: "#64748b", fontSize: 10 }}
              tickLine={false} axisLine={false} width={70} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="volume" name="出来高" fill="#334155" radius={[1, 1, 0, 0]} maxBarSize={12} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
