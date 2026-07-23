"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { MonthlyReport } from "@/lib/types";
import IncomeExpenseChart from "@/components/charts/IncomeExpenseChart";
import CategoryPieChart from "@/components/charts/CategoryPieChart";
import UserGrowthChart from "@/components/charts/UserGrowthChart";
import DailyTransactionsChart from "@/components/charts/DailyTransactionsChart";

export default function AnalyticsPage() {
  const [monthlyHistory, setMonthlyHistory] = useState<MonthlyReport[]>([]);
  const [rollupStatus, setRollupStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [categoryData, setCategoryData] = useState<{ category: string; amount: number }[]>([]);
  const [userGrowthData, setUserGrowthData] = useState<{ date: string; new_users: number }[]>([]);
  const [dailyTxnData, setDailyTxnData] = useState<{ date: string; transaction_count: number }[]>([]);

  async function load() {
    try {
      const resp = await api.get<MonthlyReport[]>("/reports/monthly-history");
      setMonthlyHistory(resp.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Couldn't load analytics data.");
    }

    try {
      const [categoryResp, growthResp, dailyResp] = await Promise.all([
        api.get("/reports/analytics/category-breakdown", { params: { period: "monthly" } }),
        api.get("/reports/analytics/user-growth", { params: { days: 30 } }),
        api.get("/reports/analytics/daily-transactions", { params: { days: 30 } }),
      ]);
      setCategoryData(categoryResp.data.map((r: any) => ({ category: r.category, amount: r.amount })));
      setUserGrowthData(growthResp.data);
      setDailyTxnData(dailyResp.data);
    } catch (err: any) {
      // Non-fatal — the page still works with just the monthly history if this fails.
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function triggerRollup() {
    setRollupStatus("Running…");
    try {
      const resp = await api.post("/reports/rollup");
      setRollupStatus(`Rolled up ${resp.data.users_processed} users for ${resp.data.month}.`);
      load();
    } catch (err: any) {
      setRollupStatus(err?.response?.data?.detail || "Rollup failed.");
    }
  }

  // Aggregate per-user monthly rows into one income/expense figure per month for the chart.
  const byMonth = new Map<string, { income: number; expense: number }>();
  for (const r of monthlyHistory) {
    const existing = byMonth.get(r.Month) || { income: 0, expense: 0 };
    existing.income += r["Total Income"];
    existing.expense += r["Total Expense"];
    byMonth.set(r.Month, existing);
  }
  const chartData = Array.from(byMonth.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([month, v]) => ({ month, income: v.income, expense: v.expense }));

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="text-sm text-ink-secondary">
          Analytics are computed from persisted rollups in the database, refreshed daily.
        </div>
        <button
          onClick={triggerRollup}
          className="h-9 px-3 rounded-lg border border-border text-sm font-medium flex items-center gap-1.5 hover:bg-canvas"
        >
          <i className="ti ti-refresh text-sm" aria-hidden="true" />
          Run rollup now
        </button>
      </div>

      {rollupStatus && <div className="text-sm text-brand-800 bg-brand-50 rounded-lg px-4 py-2.5">{rollupStatus}</div>}
      {error && <div className="text-sm text-danger-text bg-danger-bg rounded-lg px-4 py-3">{error}</div>}

      <div className="card">
        <div className="font-display font-semibold text-[13px] mb-3">Income vs expenses by month (all users)</div>
        <IncomeExpenseChart data={chartData} />
      </div>

      <div className="grid grid-cols-2 gap-5">
        <div className="card">
          <div className="font-display font-semibold text-[13px] mb-3">Spending by category (this month)</div>
          <CategoryPieChart data={categoryData} />
        </div>
        <div className="card">
          <div className="font-display font-semibold text-[13px] mb-3">User growth (last 30 days)</div>
          <UserGrowthChart data={userGrowthData} />
        </div>
      </div>

      <div className="card">
        <div className="font-display font-semibold text-[13px] mb-3">Daily transactions (last 30 days)</div>
        <DailyTransactionsChart data={dailyTxnData} />
      </div>

      <div className="card">
        <div className="font-display font-semibold text-[13px] mb-3">Monthly report history</div>
        <table className="w-full text-[13px]">
          <thead>
            <tr className="text-left text-ink-secondary text-xs">
              <th className="font-medium pb-2">Month</th>
              <th className="font-medium pb-2">User</th>
              <th className="font-medium pb-2 text-right">Income</th>
              <th className="font-medium pb-2 text-right">Expense</th>
              <th className="font-medium pb-2 text-right">Net</th>
            </tr>
          </thead>
          <tbody>
            {monthlyHistory.map((r) => (
              <tr key={r["Report ID"]} className="border-t border-border-subtle">
                <td className="py-2.5 table-figure">{r.Month}</td>
                <td className="py-2.5 text-ink-secondary">{r["User ID"]}</td>
                <td className="py-2.5 text-right table-figure text-brand">{r["Total Income"].toLocaleString()}</td>
                <td className="py-2.5 text-right table-figure text-danger">{r["Total Expense"].toLocaleString()}</td>
                <td className="py-2.5 text-right table-figure text-ink">{r.Net.toLocaleString()}</td>
              </tr>
            ))}
            {monthlyHistory.length === 0 && (
              <tr>
                <td colSpan={5} className="py-6 text-center text-ink-secondary">
                  No rollups yet — click "Run rollup now" to generate the first one.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}