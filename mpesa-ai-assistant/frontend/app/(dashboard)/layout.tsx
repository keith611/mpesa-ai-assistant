"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import Sidebar from "@/components/layout/Sidebar";
import Topbar from "@/components/layout/Topbar";

const PAGE_TITLES: Record<string, string> = {
  "/overview": "Overview",
  "/users": "Users",
  "/transactions": "Transactions",
  "/analytics": "Analytics",
  "/reports": "Reports",
  "/system": "System monitoring",
  "/settings/category-rules": "Category rules",
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-ink-secondary text-sm">
        Loading…
      </div>
    );
  }

  if (!user) return null;

  const title =
    Object.entries(PAGE_TITLES).find(([path]) => pathname?.startsWith(path))?.[1] || "Dashboard";

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 min-w-0 flex flex-col">
        <Topbar title={title} />
        <main className="flex-1 p-6 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
