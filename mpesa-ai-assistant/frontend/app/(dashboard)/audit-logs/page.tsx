"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { SystemLog } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<SystemLog[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const resp = await api.get<SystemLog[]>("/admin/audit-logs", { params: { limit: 200 } });
        setLogs(resp.data);
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Couldn't load audit logs.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-4">
      <p className="text-sm text-ink-secondary">
        Genuine admin and user actions only — automated system events (backups, scheduler, WhatsApp bot replies) are filtered out.
      </p>

      {error && <div className="text-sm text-danger-text bg-danger-bg rounded-lg px-4 py-3">{error}</div>}

      <div className="card !p-0 overflow-hidden">
        <table className="w-full text-[13px]">
          <thead>
            <tr className="text-left text-ink-secondary text-xs bg-canvas">
              <th className="font-medium py-2.5 px-4">Action</th>
              <th className="font-medium py-2.5 px-4">Actor</th>
              <th className="font-medium py-2.5 px-4">Details</th>
              <th className="font-medium py-2.5 px-4 text-right">When</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((l) => (
              <tr key={l["Log ID"]} className="border-t border-border-subtle">
                <td className="py-2.5 px-4 font-medium text-ink">{l.Event}</td>
                <td className="py-2.5 px-4 table-figure text-ink-secondary">{l.Actor}</td>
                <td className="py-2.5 px-4 text-ink-secondary">{l.Description}</td>
                <td className="py-2.5 px-4 text-right text-ink-secondary table-figure">{formatDateTime(l.Timestamp)}</td>
              </tr>
            ))}
            {!loading && logs.length === 0 && (
              <tr>
                <td colSpan={4} className="py-10 text-center text-ink-secondary">
                  No admin actions recorded yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
