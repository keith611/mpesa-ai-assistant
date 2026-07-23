"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { AppUser, Transaction } from "@/lib/types";
import { StatusBadge, CategoryBadge } from "@/components/ui/Badge";
import { formatDate, formatDateTime, formatMoney, initials } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import TransactionDetailModal from "@/components/transactions/TransactionDetailModal";

interface ActivityResponse {
  user: AppUser;
  recent_transactions: Transaction[];
  statistics: Record<string, any>;
}

export default function UserDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { hasMinRole } = useAuth();
  const userId = params.id as string;

  const [data, setData] = useState<ActivityResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [balance, setBalance] = useState<number | null>(null);
  const [selectedTxn, setSelectedTxn] = useState<Transaction | null>(null);
  const [downloading, setDownloading] = useState<"pdf" | "excel" | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const resp = await api.get<ActivityResponse>(`/reports/user-activity/${userId}`);
        setData(resp.data);
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Couldn't load this user.");
      }
      try {
        const balanceResp = await api.get(`/reports/balance/${userId}`);
        setBalance(balanceResp.data.balance);
      } catch (err: any) {
        // Non-fatal — page still works without a balance figure.
      }
    }
    load();
  }, [userId]);

  async function downloadStatement(format: "pdf" | "excel") {
    setDownloading(format);
    try {
      const resp = await api.get(`/reports/download/${format}/${userId}`, {
        params: { period: "monthly" },
        responseType: "blob",
      });
      const ext = format === "pdf" ? "pdf" : "xlsx";
      const url = window.URL.createObjectURL(new Blob([resp.data]));
      const link = document.createElement("a");
      link.href = url;
      link.download = `statement_${userId}.${ext}`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(`Couldn't generate the ${format.toUpperCase()} statement.`);
    } finally {
      setDownloading(null);
    }
  }

  if (error) return <div className="text-sm text-danger-text bg-danger-bg rounded-lg px-4 py-3">{error}</div>;
  if (!data) return <div className="text-sm text-ink-secondary">Loading…</div>;

  const { user, recent_transactions, statistics } = data;

  return (
    <div className="space-y-5">
      <button onClick={() => router.back()} className="text-sm text-ink-secondary flex items-center gap-1.5">
        <i className="ti ti-arrow-left" aria-hidden="true" /> Back to users
      </button>

      <div className="card flex items-center gap-4">
        <div className="w-14 h-14 rounded-full bg-brand-50 text-brand-800 text-lg font-semibold flex items-center justify-center flex-shrink-0">
          {initials(user["Full Name"])}
        </div>
        <div className="flex-1">
          <div className="font-display font-semibold text-lg text-ink">{user["Full Name"]}</div>
          <div className="text-sm text-ink-secondary">
            {user["Phone Number"]} · WhatsApp {user["WhatsApp Number"]}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status={user.Status} />
          <span className="badge bg-canvas text-ink-secondary">{user.Role}</span>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-3">
        <div className="card">
          <div className="text-xs text-ink-secondary mb-1.5">Transactions</div>
          <div className="font-mono text-lg font-medium">{statistics["Total Transactions"] ?? 0}</div>
        </div>
        <div className="card">
          <div className="text-xs text-ink-secondary mb-1.5">Total spent</div>
          <div className="font-mono text-lg font-medium text-danger">{formatMoney(statistics["Total Spent"])}</div>
        </div>
        <div className="card">
          <div className="text-xs text-ink-secondary mb-1.5">Total received</div>
          <div className="font-mono text-lg font-medium text-brand">{formatMoney(statistics["Total Received"])}</div>
        </div>
        <div className="card">
          <div className="text-xs text-ink-secondary mb-1.5">Current balance</div>
          <div className="font-mono text-lg font-medium">{balance != null ? formatMoney(balance) : "—"}</div>
        </div>
        <div className="card">
          <div className="text-xs text-ink-secondary mb-1.5">Registered</div>
          <div className="text-sm font-medium pt-1.5">{formatDate(user["Registration Date"])}</div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="text-xs text-ink-secondary">Last login: {formatDate(user["Last Activity"])}</div>
        <div className="flex gap-2">
          <button
            onClick={() => downloadStatement("pdf")}
            disabled={downloading !== null}
            className="h-9 px-3 rounded-lg bg-brand hover:bg-brand-hover text-white text-sm font-medium flex items-center gap-1.5 disabled:opacity-60"
          >
            <i className="ti ti-file-type-pdf text-sm" aria-hidden="true" />
            {downloading === "pdf" ? "Generating…" : "Download PDF"}
          </button>
          <button
            onClick={() => downloadStatement("excel")}
            disabled={downloading !== null}
            className="h-9 px-3 rounded-lg border border-border text-sm font-medium flex items-center gap-1.5 hover:bg-canvas disabled:opacity-60"
          >
            <i className="ti ti-file-spreadsheet text-sm" aria-hidden="true" />
            {downloading === "excel" ? "Generating…" : "Download Excel"}
          </button>
        </div>
      </div>

      <div className="card">
        <div className="font-display font-semibold text-[13px] mb-3">Recent transactions</div>
        <table className="w-full text-[13px]">
          <thead>
            <tr className="text-left text-ink-secondary text-xs">
              <th className="font-medium pb-2">Date</th>
              <th className="font-medium pb-2">Type</th>
              <th className="font-medium pb-2">Category</th>
              <th className="font-medium pb-2">Code</th>
              <th className="font-medium pb-2 text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            {recent_transactions.map((t) => (
              <tr
                key={t["Transaction ID"]}
                onClick={() => setSelectedTxn(t)}
                className="border-t border-border-subtle cursor-pointer hover:bg-canvas"
              >
                <td className="py-2.5 text-ink-secondary table-figure">{formatDateTime(t.Timestamp)}</td>
                <td className="py-2.5 text-ink-secondary">{t["Transaction Type"]}</td>
                <td className="py-2.5">
                  <CategoryBadge category={t.Category} />
                </td>
                <td className="py-2.5 table-figure text-ink-secondary">{t["Transaction Code"]}</td>
                <td className="py-2.5 text-right table-figure text-ink">{formatMoney(t.Amount)}</td>
              </tr>
            ))}
            {recent_transactions.length === 0 && (
              <tr>
                <td colSpan={5} className="py-6 text-center text-ink-secondary">
                  No transactions yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {selectedTxn && <TransactionDetailModal transaction={selectedTxn} onClose={() => setSelectedTxn(null)} />}
    </div>
  );
}