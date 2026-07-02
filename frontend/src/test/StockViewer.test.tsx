import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import StockViewer from "@/components/StockViewer";
import * as api from "@/lib/api";

vi.mock("recharts", () => ({
  ComposedChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Line: () => null,
  Bar: () => null,
  XAxis: () => null,
  YAxis: () => null,
  CartesianGrid: () => null,
  Tooltip: () => null,
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

const MOCK_DATA: api.DailyBar[] = [
  { date: "2024-01-04", open: 2400, high: 2450, low: 2390, close: 2420, volume: 9000000 },
  { date: "2024-01-05", open: 2500, high: 2600, low: 2480, close: 2550, volume: 10000000 },
];
const MOCK_INFO: api.StockInfo = {
  code: "72030", name: "トヨタ自動車", name_english: "Toyota Motor Corporation",
  sector: "輸送用機器", market: "プライム",
};

describe("StockViewer", () => {
  beforeEach(() => { vi.restoreAllMocks(); });

  it("renders search input and button", () => {
    render(<StockViewer />);
    expect(screen.getByPlaceholderText(/銘柄コード/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /検索/ })).toBeInTheDocument();
  });

  it("shows empty state initially", () => {
    render(<StockViewer />);
    expect(screen.getByText(/銘柄コードを入力して検索してください/)).toBeInTheDocument();
  });

  it("disables search button when input is empty", () => {
    render(<StockViewer />);
    expect(screen.getByRole("button", { name: /検索/ })).toBeDisabled();
  });

  it("displays stock data after search", async () => {
    vi.spyOn(api, "fetchStockPrices").mockResolvedValue({ code: "7203", data: MOCK_DATA });
    vi.spyOn(api, "fetchStockInfo").mockResolvedValue(MOCK_INFO);
    render(<StockViewer />);
    fireEvent.change(screen.getByPlaceholderText(/銘柄コード/), { target: { value: "7203" } });
    fireEvent.click(screen.getByRole("button", { name: /検索/ }));
    await waitFor(() => expect(screen.getByText("トヨタ自動車")).toBeInTheDocument());
    expect(screen.getByText(/2,550/)).toBeInTheDocument();
  });

  it("shows error on API failure", async () => {
    vi.spyOn(api, "fetchStockPrices").mockRejectedValue(new Error("No price data found for code '9999'"));
    vi.spyOn(api, "fetchStockInfo").mockRejectedValue(new Error("not found"));
    render(<StockViewer />);
    fireEvent.change(screen.getByPlaceholderText(/銘柄コード/), { target: { value: "9999" } });
    fireEvent.click(screen.getByRole("button", { name: /検索/ }));
    await waitFor(() => expect(screen.getByText(/No price data found/)).toBeInTheDocument());
  });

  it("shows period selector after successful search", async () => {
    vi.spyOn(api, "fetchStockPrices").mockResolvedValue({ code: "7203", data: MOCK_DATA });
    vi.spyOn(api, "fetchStockInfo").mockResolvedValue(MOCK_INFO);
    render(<StockViewer />);
    fireEvent.change(screen.getByPlaceholderText(/銘柄コード/), { target: { value: "7203" } });
    fireEvent.click(screen.getByRole("button", { name: /検索/ }));
    await waitFor(() => {
      expect(screen.getByText("1ヶ月")).toBeInTheDocument();
      expect(screen.getByText("3ヶ月")).toBeInTheDocument();
      expect(screen.getByText("1年")).toBeInTheDocument();
    });
  });
});
