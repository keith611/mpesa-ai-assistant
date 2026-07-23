"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { useAuth } from "@/lib/auth-context";

const NAV_ITEMS = [
  { href: "/overview", label: "Overview", icon: "layout-dashboard", minRole: "SUPPORT" as const },
  { href: "/search", label: "Search", icon: "search", minRole: "SUPPORT" as const },
  { href: "/users", label: "Users", icon: "users", minRole: "SUPPORT" as const },
  { href: "/transactions", label: "Transactions", icon: "receipt", minRole: "SUPPORT" as const },
  { href: "/analytics", label: "Analytics", icon: "chart-bar", minRole: "SUPPORT" as const },
  { href: "/reports", label: "Reports", icon: "file-report", minRole: "SUPPORT" as const },
  { href: "/system", label: "System", icon: "server-2", minRole: "ADMIN" as const },
  { href: "/settings/category-rules", label: "Category rules", icon: "adjustments", minRole: "ADMIN" as const },
  { href: "/audit-logs", label: "Audit logs", icon: "history", minRole: "ADMIN" as const },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { hasMinRole } = useAuth();

  return (
    <aside className="w-[208px] bg-sidebar flex-shrink-0 flex flex-col py-5 px-3.5">
      <div className="px-2 mb-6">
        <div className="font-display font-bold text-[15px] text-white leading-tight">M-Pesa AI</div>
        <div className="text-[11px] text-sidebar-text">Admin console</div>
      </div>
      <nav className="flex flex-col gap-0.5">
        {NAV_ITEMS.filter((item) => hasMinRole(item.minRole)).map((item) => {
          const active = pathname?.startsWith(item.href);
          return (
            <Link key={item.href} href={item.href} className={clsx("nav-item", active && "nav-item-active")}>
              <i className={`ti ti-${item.icon} text-base`} aria-hidden="true" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
