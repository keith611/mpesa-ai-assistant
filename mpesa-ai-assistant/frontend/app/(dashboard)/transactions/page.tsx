"use client";

import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import { PaginatedTransactions, Transaction } from "@/lib/types";
import { CategoryBadge } from "@/components/ui/Badge";
import { formatDateTime, formatMoney } from "@/lib/utils";
import TransactionDetailModal from "@/components/transactions/TransactionDetailModal";

const CATEGORIES = [
  "Food", "Transport", "Fuel", "Rent", "Utilities", "Business",
  "Shopping", "Entertainment", "Education", "Healthcare", "Other",
];

export default function TransactionsPage() {
  const [data, setData] = useState<PaginatedTransactions | null>(null);
  const [keyword, setKeyword] = useState("");
  const [category, setCategory] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [selectedTxn, setSelectedTxn] = useState<Transaction | null>(null);
  const pageSize = 20;

  const load = useCallback(async () => {
    try {
      const resp = await api.get<PaginatedTransactions>("/transactions", {
        params: {
          keyword: keyword || undefined,
          category: category || undefined,
          date_from: dateFrom || undefined,
          date_to: dateTo || undefined,
          page,
          page_size: pageSize,
        },
      });
      setData(resp.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Couldn't load transactions.");
    }
  }, [keyword, category, dateFrom, dateTo, page]);

  useEffect(() => {
    load();
  }, [load]);

  async function exportCsv() {
    try {
      const resp = await api.get("/transactions/export/csv", {
        params: { date_from: dateFrom || undefined, date_to: dateTo || undefined },
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([resp.data]));
      const link = document.createElement("a");
      link.href = url;
      link.download = "transactions_export.csv";
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert("Couldn't export transactions. You may need Admin or Support access.");
    }
  }

  const totalPages = data ? Math.max(1, Math.ceil(data.total / pageSize)) : 1;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <input
          type="text"
          placeholder="Search sender, receiver, or code"
          value={keyword}
          onChange={(e) => {
            setPage(1);
            setKeyword(e.target.value);
          }}
          className="h-9 px-3 rounded-lg border border-border text-sm w-64 focus:outline-none focus:ring-2 focus:ring-brand/30"
        />
        <select
          value={category}
          onChange={(e) => {
            setPage(1);
            setCategory(e.target.value);
          }}
          className="h-9 px-3 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-brand/30"
        >
          <option value="">All categories</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <input
          type="date"
          value={dateFrom}
          onChange={(e) => {
            setPage(1);
            setDateFrom(e.target.value);
          }}
          className="h-9 px-3 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-brand/30"
        />
        <span className="text-ink-secondary text-sm">to</span>
        <input
          type="date"
          value={dateTo}
          onChange={(e) => {
            setPage(1);
            setDateTo(e.target.value);
          }}
          className="h-9 px-3 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-brand/30"
        />
        <button
          onClick={exportCsv}
          className="h-9 px-3 rounded-lg border border-border text-sm font-medium flex items-center gap-1.5 ml-auto hover:bg-canvas"
        >
          <i className="ti ti-download text-sm" aria-hidden="true" />
          Export CSV
        </button>
      </div>

      {error && <div className="text-sm text-danger-text bg-danger-bg rounded-lg px-4 py-3">{error}</div>}

      <div className="card !p-0 overflow-hidden">
        <table className="w-full text-[13px]">
          <thead>
            <tr className="text-left text-ink-secondary text-xs bg-canvas">
              <th className="font-medium py-2.5 px-4">Date</th>
              <th className="font-medium py-2.5 px-4">User</th>
              <th className="font-medium py-2.5 px-4">Type</th>
              <th className="font-medium py-2.5 px-4">Category</th>
              <th className="font-medium py-2.5 px-4">Code</th>
              <th className="font-medium py-2.5 px-4 text-right">Amount</th>
              <th className="font-medium py-2.5 px-4 text-right">Balance</th>
            </tr>
          </thead>
          <tbody>
            {data?.transactions.map((t) => (
              <tr
                key={t["Transaction ID"]}
                onClick={() => setSelectedTxn(t)}
                className="border-t border-border-subtle cursor-pointer hover:bg-canvas"
              >
                <td className="py-2.5 px-4 text-ink-secondary table-figure">{formatDateTime(t.Timestamp)}</td>
                <td className="py-2.5 px-4 text-ink">{t["User ID"]}</td>
                <td className="py-2.5 px-4 text-ink-secondary">{t["Transaction Type"]}</td>
                <td className="py-2.5 px-4">
                  <CategoryBadge category={t.Category} />
                </td>
                <td className="py-2.5 px-4 table-figure text-ink-secondary">{t["Transaction Code"]}</td>
                <td className="py-2.5 px-4 text-right table-figure text-ink">{formatMoney(t.Amount)}</td>
                <td className="py-2.5 px-4 text-right table-figure text-ink-secondary">
                  {t.Balance != null ? formatMoney(t.Balance) : "—"}
                </td>
              </tr>
            ))}
            {data && data.transactions.length === 0 && (
              <tr>
                <td colSpan={7} className="py-8 text-center text-ink-secondary">
                  No transactions match your filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {data && data.total > pageSize && (
        <div className="flex items-center justify-between text-sm text-ink-secondary">
          <span>
            Page {page} of {totalPages} · {data.total} transactions
          </span>
          <div className="flex gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="h-8 px-3 rounded-lg border border-border disabled:opacity-40"
            >
              Previous
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              className="h-8 px-3 rounded-lg border border-border disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {selectedTxn && <TransactionDetailModal transaction={selectedTxn} onClose={() => setSelectedTxn(null)} />}
    </div>
  );
}