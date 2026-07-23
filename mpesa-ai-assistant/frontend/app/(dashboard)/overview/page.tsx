"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Overview, PaginatedTransactions } from "@/lib/types";
import StatCard from "@/components/ui/StatCard";
import { CategoryBadge } from "@/components/ui/Badge";
import { formatCompactMoney, formatMoney, formatDateTime } from "@/lib/utils";

export default function OverviewPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [recentTxns, setRecentTxns] = useState<PaginatedTransactions | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [overviewResp, txnsResp] = await Promise.all([
          api.get<Overview>("/reports/overview"),
          api.get<PaginatedTransactions>("/transactions?page=1&page_size=8"),
        ]);
        setOverview(overviewResp.data);
        setRecentTxns(txnsResp.data);
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Couldn't load overview data.");
      }
    }
    load();
  }, []);

  if (error) {
    return <div className="text-sm text-danger-text bg-danger-bg rounded-lg px-4 py-3">{error}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-3">
        <StatCard label="Total users" value={overview ? overview.total_users.toLocaleString() : "—"} />
        <StatCard label="Active users" value={overview ? overview.active_users.toLocaleString() : "—"} />
        <StatCard label="New users today" value={overview ? overview.new_users_today.toLocaleString() : "—"} />
        <StatCard label="Total transactions" value={overview ? overview.total_transactions.toLocaleString() : "—"} />
        <StatCard
          label="Total income"
          value={overview ? formatCompactMoney(overview.total_income) : "—"}
          tone="positive"
        />
        <StatCard
          label="Total expenses"
          value={overview ? formatCompactMoney(overview.total_expenses) : "—"}
          tone="negative"
        />
        <StatCard
          label="Net"
          value={overview ? formatCompactMoney(overview.total_income - overview.total_expenses) : "—"}
        />
        <StatCard
          label="Avg. transaction"
          value={
            overview && overview.total_transactions > 0
              ? formatCompactMoney((overview.total_income + overview.total_expenses) / overview.total_transactions)
              : "—"
          }
        />
      </div>

      <div className="card">
        <div className="font-display font-semibold text-[13px] mb-3">Recent transactions</div>
        <table className="w-full text-[13px]">
          <thead>
            <tr className="text-left text-ink-secondary text-xs">
              <th className="font-medium pb-2">User</th>
              <th className="font-medium pb-2">Type</th>
              <th className="font-medium pb-2">Category</th>
              <th className="font-medium pb-2">Date</th>
              <th className="font-medium pb-2 text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            {recentTxns?.transactions.map((t) => (
              <tr key={t["Transaction ID"]} className="border-t border-border-subtle">
                <td className="py-2.5 text-ink">{t["User ID"]}</td>
                <td className="py-2.5 text-ink-secondary">{t["Transaction Type"]}</td>
                <td className="py-2.5">
                  <CategoryBadge category={t.Category} />
                </td>
                <td className="py-2.5 text-ink-secondary table-figure">{formatDateTime(t.Timestamp)}</td>
                <td className="py-2.5 text-right table-figure text-ink">{formatMoney(t.Amount)}</td>
              </tr>
            ))}
            {recentTxns && recentTxns.transactions.length === 0 && (
              <tr>
                <td colSpan={5} className="py-6 text-center text-ink-secondary">
                  No transactions recorded yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
