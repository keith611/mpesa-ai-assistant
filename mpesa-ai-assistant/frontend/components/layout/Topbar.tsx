"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { initials } from "@/lib/utils";
import clsx from "clsx";

interface HealthState {
  api: "up" | "down";
  whatsapp: "up" | "warn" | "down";
  smsSync: "up" | "warn" | "down";
  backup: "up" | "warn" | "down";
}

function Dot({ state }: { state: "up" | "warn" | "down" }) {
  return (
    <span
      className={clsx("status-dot", {
        "bg-success": state === "up",
        "bg-warning": state === "warn",
        "bg-danger": state === "down",
      })}
    />
  );
}

export default function Topbar({ title }: { title: string }) {
  const { user, logout } = useAuth();
  const [health, setHealth] = useState<HealthState>({ api: "down", whatsapp: "down", smsSync: "warn", backup: "up" });

  useEffect(() => {
    let cancelled = false;
    async function poll() {
      try {
        await api.get("/health");
        if (!cancelled) setHealth((h) => ({ ...h, api: "up" }));
      } catch {
        if (!cancelled) setHealth((h) => ({ ...h, api: "down" }));
      }
      try {
        const resp = await api.get("/whatsapp/outbox?limit=1");
        if (!cancelled) setHealth((h) => ({ ...h, whatsapp: resp.status === 200 ? "up" : "warn" }));
      } catch {
        if (!cancelled) setHealth((h) => ({ ...h, whatsapp: "warn" }));
      }
    }
    poll();
    const interval = setInterval(poll, 30000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="h-[57px] flex items-center justify-between px-6 border-b border-border bg-surface flex-shrink-0">
      <div className="font-display font-semibold text-[16px] text-ink">{title}</div>
      <div className="flex items-center gap-5">
        <div className="flex items-center gap-3.5 text-[11px] text-ink-secondary">
          <span className="flex items-center gap-1.5">
            <Dot state={health.api} /> API
          </span>
          <span className="flex items-center gap-1.5">
            <Dot state={health.whatsapp} /> WhatsApp
          </span>
          <span className="flex items-center gap-1.5">
            <Dot state={health.smsSync} /> SMS sync
          </span>
          <span className="flex items-center gap-1.5">
            <Dot state={health.backup} /> Backup
          </span>
        </div>
        <div className="relative group">
          <button className="w-7 h-7 rounded-full bg-brand-50 text-brand-800 text-[11px] font-semibold flex items-center justify-center">
            {initials(user?.["Full Name"])}
          </button>
          <div className="absolute right-0 top-9 w-44 bg-surface border border-border rounded-lg shadow-sm py-1 hidden group-hover:block z-10">
            <div className="px-3 py-2 border-b border-border-subtle">
              <div className="text-sm font-medium text-ink truncate">{user?.["Full Name"]}</div>
              <div className="text-xs text-ink-secondary">{user?.Role}</div>
            </div>
            <button
              onClick={logout}
              className="w-full text-left px-3 py-2 text-sm text-danger-text hover:bg-danger-bg flex items-center gap-2"
            >
              <i className="ti ti-logout text-sm" aria-hidden="true" />
              Sign out
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
