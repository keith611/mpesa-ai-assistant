"use client";

import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import { BackupSnapshot, SystemLog } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

interface SmsSyncStatus {
  last_sms_received_at: string | null;
  synced_today: number;
}

interface StorageUsage {
  users: number;
  transactions: number;
  system_logs: number;
}

export default function SystemPage() {
  const [backups, setBackups] = useState<BackupSnapshot[]>([]);
  const [logs, setLogs] = useState<SystemLog[]>([]);
  const [errors, setErrors] = useState<SystemLog[]>([]);
  const [runningTier, setRunningTier] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [smsSync, setSmsSync] = useState<SmsSyncStatus | null>(null);
  const [storage, setStorage] = useState<StorageUsage | null>(null);

  const load = useCallback(async () => {
    try {
      const [backupsResp, logsResp, errorsResp] = await Promise.all([
        api.get<BackupSnapshot[]>("/admin/backups"),
        api.get<SystemLog[]>("/reports/system/logs", { params: { limit: 30 } }),
        api.get<SystemLog[]>("/reports/system/errors", { params: { limit: 10 } }),
      ]);
      setBackups(backupsResp.data);
      setLogs(logsResp.data);
      setErrors(errorsResp.data);
    } catch {
      // Silently ignore — user may lack ADMIN role for some of these.
    }

    try {
      const [smsResp, storageResp] = await Promise.all([
        api.get<SmsSyncStatus>("/reports/system/sms-sync-status"),
        api.get<StorageUsage>("/reports/system/storage-usage"),
      ]);
      setSmsSync(smsResp.data);
      setStorage(storageResp.data);
    } catch {
      // Non-fatal — rest of the page still works.
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function runBackup(tier: "hourly" | "daily" | "weekly") {
    setRunningTier(tier);
    try {
      const resp = await api.post(`/admin/backups/run/${tier}`);
      setMessage(`${tier} backup created: ${resp.data.files.length} files.`);
      load();
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || "Backup failed.");
    } finally {
      setRunningTier(null);
    }
  }

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-3">
        <div className="card">
          <div className="text-xs text-ink-secondary mb-1">SMS sync</div>
          <div className="text-sm font-medium">{smsSync?.synced_today ?? 0} synced today</div>
          <div className="text-xs text-ink-secondary mt-1">
            Last received: {smsSync?.last_sms_received_at ? formatDateTime(smsSync.last_sms_received_at) : "never"}
          </div>
        </div>
        <div className="card">
          <div className="text-xs text-ink-secondary mb-1">Storage (row counts)</div>
          <div className="text-sm font-medium">
            {storage?.users ?? 0} users · {storage?.transactions ?? 0} transactions · {storage?.system_logs ?? 0} logs
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {(["hourly", "daily", "weekly"] as const).map((tier) => (
          <div key={tier} className="card flex items-center justify-between">
            <div>
              <div className="text-xs text-ink-secondary capitalize mb-1">{tier} backups</div>
              <div className="text-lg font-mono font-medium">
                {backups.filter((b) => b.tier === tier).length}
              </div>
            </div>
            <button
              onClick={() => runBackup(tier)}
              disabled={runningTier !== null}
              className="h-8 px-3 rounded-lg border border-border text-xs font-medium hover:bg-canvas disabled:opacity-50"
            >
              {runningTier === tier ? "Running…" : "Run now"}
            </button>
          </div>
        ))}
      </div>

      {message && <div className="text-sm text-brand-800 bg-brand-50 rounded-lg px-4 py-2.5">{message}</div>}

      <div className="grid grid-cols-2 gap-5">
        <div className="card">
          <div className="font-display font-semibold text-[13px] mb-3">Backup snapshots</div>
          <div className="space-y-2 max-h-80 overflow-auto">
            {backups.map((b) => (
              <div key={`${b.tier}-${b.snapshot}`} className="flex items-center justify-between text-[13px] border-b border-border-subtle pb-2">
                <div>
                  <div className="font-mono text-ink">{b.snapshot}</div>
                  <div className="text-xs text-ink-secondary capitalize">{b.tier} · {b.files.length} files</div>
                </div>
                <div className="text-xs text-ink-secondary table-figure">{formatBytes(b.size_bytes)}</div>
              </div>
            ))}
            {backups.length === 0 && <div className="text-sm text-ink-secondary py-4 text-center">No backups yet.</div>}
          </div>
        </div>

        <div className="card">
          <div className="font-display font-semibold text-[13px] mb-3">Recent errors</div>
          <div className="space-y-2 max-h-80 overflow-auto">
            {errors.map((e) => (
              <div key={e["Log ID"]} className="text-[13px] border-b border-border-subtle pb-2">
                <div className="flex items-center justify-between">
                  <span className="badge bg-danger-bg text-danger-text">{e.Event}</span>
                  <span className="text-xs text-ink-secondary table-figure">{formatDateTime(e.Timestamp)}</span>
                </div>
                <div className="text-xs text-ink-secondary mt-1">{e.Description}</div>
              </div>
            ))}
            {errors.length === 0 && <div className="text-sm text-ink-secondary py-4 text-center">No errors logged. Good sign.</div>}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="font-display font-semibold text-[13px] mb-3">System activity log</div>
        <table className="w-full text-[13px]">
          <thead>
            <tr className="text-left text-ink-secondary text-xs">
              <th className="font-medium pb-2">Event</th>
              <th className="font-medium pb-2">Status</th>
              <th className="font-medium pb-2">Actor</th>
              <th className="font-medium pb-2">Description</th>
              <th className="font-medium pb-2 text-right">Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((l) => (
              <tr key={l["Log ID"]} className="border-t border-border-subtle">
                <td className="py-2 text-ink font-medium">{l.Event}</td>
                <td className="py-2">
                  <span className={`badge ${l.Status === "ERROR" ? "bg-danger-bg text-danger-text" : "bg-success-bg text-success-text"}`}>
                    {l.Status}
                  </span>
                </td>
                <td className="py-2 text-ink-secondary table-figure">{l.Actor}</td>
                <td className="py-2 text-ink-secondary">{l.Description}</td>
                <td className="py-2 text-right text-ink-secondary table-figure">{formatDateTime(l.Timestamp)}</td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr>
                <td colSpan={5} className="py-6 text-center text-ink-secondary">
                  No activity logged yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}