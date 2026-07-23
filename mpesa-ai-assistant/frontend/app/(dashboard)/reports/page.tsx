"use client";

import { useState } from "react";
import { api } from "@/lib/api";

const PERIODS = ["daily", "weekly", "monthly", "annual"] as const;

export default function ReportsPage() {
  const [userId, setUserId] = useState("");
  const [period, setPeriod] = useState<(typeof PERIODS)[number]>("monthly");
  const [downloading, setDownloading] = useState<"pdf" | "excel" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function download(format: "pdf" | "excel") {
    if (!userId.trim()) {
      setError("Enter a User ID first (e.g. USR-000001).");
      return;
    }
    setError(null);
    setDownloading(format);
    try {
      const resp = await api.get(`/reports/download/${format}/${userId}`, {
        params: { period },
        responseType: "blob",
      });
      const ext = format === "pdf" ? "pdf" : "xlsx";
      const url = window.URL.createObjectURL(new Blob([resp.data]));
      const link = document.createElement("a");
      link.href = url;
      link.download = `statement_${userId}_${period}.${ext}`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err?.response?.data?.detail || `Couldn't generate the ${format.toUpperCase()} report.`);
    } finally {
      setDownloading(null);
    }
  }

  return (
    <div className="space-y-5 max-w-xl">
      <div className="card">
        <div className="font-display font-semibold text-[13px] mb-1">Generate a user statement</div>
        <p className="text-sm text-ink-secondary mb-4">
          Produces a formatted PDF or Excel statement for a single user over the selected period.
        </p>

        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-ink mb-1.5">User ID</label>
            <input
              type="text"
              placeholder="USR-000001"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="w-full h-10 px-3 rounded-lg border border-border text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand/30"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-ink mb-1.5">Period</label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value as any)}
              className="w-full h-10 px-3 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-brand/30"
            >
              {PERIODS.map((p) => (
                <option key={p} value={p}>
                  {p[0].toUpperCase() + p.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {error && <div className="mt-3 text-sm text-danger-text bg-danger-bg rounded-lg px-3 py-2">{error}</div>}

        <div className="flex gap-2 mt-4">
          <button
            onClick={() => download("pdf")}
            disabled={downloading !== null}
            className="h-10 px-4 rounded-lg bg-brand hover:bg-brand-hover text-white text-sm font-medium flex items-center gap-2 disabled:opacity-60"
          >
            <i className="ti ti-file-type-pdf text-base" aria-hidden="true" />
            {downloading === "pdf" ? "Generating…" : "Download PDF"}
          </button>
          <button
            onClick={() => download("excel")}
            disabled={downloading !== null}
            className="h-10 px-4 rounded-lg border border-border text-sm font-medium flex items-center gap-2 hover:bg-canvas disabled:opacity-60"
          >
            <i className="ti ti-file-spreadsheet text-base" aria-hidden="true" />
            {downloading === "excel" ? "Generating…" : "Download Excel"}
          </button>
        </div>
      </div>

      <div className="card">
        <div className="font-display font-semibold text-[13px] mb-1">System-wide reports</div>
        <p className="text-sm text-ink-secondary">
          For system-wide transaction exports across all users, use the <span className="font-medium">Transactions</span>{" "}
          page and its Export CSV button with your desired date range.
        </p>
      </div>
    </div>
  );
}
