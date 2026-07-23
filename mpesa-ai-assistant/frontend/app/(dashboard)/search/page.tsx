"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { CategoryBadge, StatusBadge } from "@/components/ui/Badge";
import { formatMoney, initials } from "@/lib/utils";

interface SearchResult {
  users: any[];
  transactions: any[];
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSearch(e: FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await api.get<SearchResult>("/admin/search", { params: { q: query } });
      setResults(resp.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Search failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          placeholder="Search by user ID, phone number, transaction code, amount, category, sender, receiver..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 h-10 px-3 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-brand/30"
        />
        <button
          type="submit"
          disabled={loading}
          className="h-10 px-4 rounded-lg bg-brand hover:bg-brand-hover text-white text-sm font-medium disabled:opacity-60"
        >
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {error && <div className="text-sm text-danger-text bg-danger-bg rounded-lg px-4 py-3">{error}</div>}

      {results && (
        <div className="space-y-5">
          <div className="card">
            <div className="font-display font-semibold text-[13px] mb-3">
              Users {results.users.length > 0 && `(${results.users.length})`}
            </div>
            {results.users.length === 0 ? (
              <div className="text-sm text-ink-secondary py-2">No matching users.</div>
            ) : (
              <div className="space-y-2">
                {results.users.map((u) => (
                  <Link
                    key={u["User ID"]}
                    href={`/users/${u["User ID"]}`}
                    className="flex items-center gap-3 py-2 border-t border-border-subtle first:border-t-0 hover:bg-canvas -mx-2 px-2 rounded"
                  >
                    <span className="w-8 h-8 rounded-full bg-brand-50 text-brand-800 text-xs font-semibold flex items-center justify-center flex-shrink-0">
                      {initials(u["Full Name"])}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-ink">{u["Full Name"]}</div>
                      <div className="text-xs text-ink-secondary table-figure">{u["Phone Number"]}</div>
                    </div>
                    <StatusBadge status={u.Status} />
                  </Link>
                ))}
              </div>
            )}
          </div>

          <div className="card">
            <div className="font-display font-semibold text-[13px] mb-3">
              Transactions {results.transactions.length > 0 && `(${results.transactions.length})`}
            </div>
            {results.transactions.length === 0 ? (
              <div className="text-sm text-ink-secondary py-2">No matching transactions.</div>
            ) : (
              <table className="w-full text-[13px]">
                <tbody>
                  {results.transactions.map((t) => (
                    <tr key={t["Transaction ID"]} className="border-t border-border-subtle">
                      <td className="py-2.5 table-figure text-ink-secondary">{t["Transaction Code"]}</td>
                      <td className="py-2.5 text-ink">{t["User ID"]}</td>
                      <td className="py-2.5 text-ink-secondary">{t["Transaction Type"]}</td>
                      <td className="py-2.5">
                        <CategoryBadge category={t.Category} />
                      </td>
                      <td className="py-2.5 text-right table-figure text-ink">{formatMoney(t.Amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
