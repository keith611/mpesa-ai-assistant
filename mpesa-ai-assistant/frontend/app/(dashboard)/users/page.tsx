"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { PaginatedUsers } from "@/lib/types";
import { StatusBadge } from "@/components/ui/Badge";
import { formatDate, initials } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import CreateUserModal from "@/components/users/CreateUserModal";

export default function UsersPage() {
  const { hasMinRole } = useAuth();
  const [data, setData] = useState<PaginatedUsers | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const pageSize = 15;

  const load = useCallback(async () => {
    try {
      const resp = await api.get<PaginatedUsers>("/users", {
        params: { search: search || undefined, status: statusFilter || undefined, page, page_size: pageSize },
      });
      setData(resp.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Couldn't load users.");
    }
  }, [search, statusFilter, page]);

  useEffect(() => {
    load();
  }, [load]);

  async function toggleStatus(userId: string, current: string) {
    const action = current === "ACTIVE" ? "suspend" : "activate";
    try {
      await api.post(`/users/${userId}/${action}`);
      load();
    } catch (err: any) {
      alert(err?.response?.data?.detail || `Couldn't ${action} user.`);
    }
  }

  async function resetPassword(userId: string, fullName: string) {
    if (!confirm(`Generate a new temporary password for ${fullName}? Their current password will stop working immediately.`)) {
      return;
    }
    try {
      const resp = await api.post(`/users/${userId}/reset-password`);
      alert(`New temporary password for ${fullName}:\n\n${resp.data.temporary_password}\n\nShare this with them through a trusted channel. They should change it after signing in.`);
    } catch (err: any) {
      alert(err?.response?.data?.detail || "Couldn't reset password.");
    }
  }

  const totalPages = data ? Math.max(1, Math.ceil(data.total / pageSize)) : 1;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <input
          type="text"
          placeholder="Search by name or phone number"
          value={search}
          onChange={(e) => {
            setPage(1);
            setSearch(e.target.value);
          }}
          className="h-9 px-3 rounded-lg border border-border text-sm w-72 focus:outline-none focus:ring-2 focus:ring-brand/30"
        />
        <select
          value={statusFilter}
          onChange={(e) => {
            setPage(1);
            setStatusFilter(e.target.value);
          }}
          className="h-9 px-3 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-brand/30"
        >
          <option value="">All statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="SUSPENDED">Suspended</option>
          <option value="PENDING">Pending</option>
          <option value="DELETED">Deleted</option>
        </select>
        <div className="text-sm text-ink-secondary ml-auto">{data ? `${data.total} users` : ""}</div>
        {hasMinRole("ADMIN") && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="h-9 px-3 rounded-lg bg-brand hover:bg-brand-hover text-white text-sm font-medium flex items-center gap-1.5"
          >
            <i className="ti ti-plus text-sm" aria-hidden="true" />
            Create user
          </button>
        )}
      </div>

      {showCreateModal && (
        <CreateUserModal onClose={() => setShowCreateModal(false)} onCreated={load} />
      )}

      {error && <div className="text-sm text-danger-text bg-danger-bg rounded-lg px-4 py-3">{error}</div>}

      <div className="card !p-0 overflow-hidden">
        <table className="w-full text-[13px]">
          <thead>
            <tr className="text-left text-ink-secondary text-xs bg-canvas">
              <th className="font-medium py-2.5 px-4">User</th>
              <th className="font-medium py-2.5 px-4">Phone</th>
              <th className="font-medium py-2.5 px-4">Role</th>
              <th className="font-medium py-2.5 px-4">Status</th>
              <th className="font-medium py-2.5 px-4">Registered</th>
              <th className="font-medium py-2.5 px-4">Last activity</th>
              <th className="font-medium py-2.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {data?.users.map((u) => (
              <tr key={u["User ID"]} className="border-t border-border-subtle">
                <td className="py-2.5 px-4">
                  <Link href={`/users/${u["User ID"]}`} className="flex items-center gap-2.5 hover:underline">
                    <span className="w-7 h-7 rounded-full bg-brand-50 text-brand-800 text-[11px] font-semibold flex items-center justify-center flex-shrink-0">
                      {initials(u["Full Name"])}
                    </span>
                    <span className="text-ink font-medium">{u["Full Name"]}</span>
                  </Link>
                </td>
                <td className="py-2.5 px-4 table-figure text-ink-secondary">{u["Phone Number"]}</td>
                <td className="py-2.5 px-4 text-ink-secondary">{u.Role}</td>
                <td className="py-2.5 px-4">
                  <StatusBadge status={u.Status} />
                </td>
                <td className="py-2.5 px-4 text-ink-secondary">{formatDate(u["Registration Date"])}</td>
                <td className="py-2.5 px-4 text-ink-secondary">{formatDate(u["Last Activity"])}</td>
                <td className="py-2.5 px-4 text-right space-x-3">
                  {hasMinRole("ADMIN") && u.Status !== "DELETED" && (
                    <>
                      <button
                        onClick={() => resetPassword(u["User ID"], u["Full Name"])}
                        className="text-xs font-medium text-ink-secondary hover:text-ink"
                      >
                        Reset password
                      </button>
                      <button
                        onClick={() => toggleStatus(u["User ID"], u.Status)}
                        className="text-xs font-medium text-brand hover:text-brand-hover"
                      >
                        {u.Status === "ACTIVE" ? "Suspend" : "Activate"}
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
            {data && data.users.length === 0 && (
              <tr>
                <td colSpan={7} className="py-8 text-center text-ink-secondary">
                  No users match your filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {data && data.total > pageSize && (
        <div className="flex items-center justify-between text-sm text-ink-secondary">
          <span>
            Page {page} of {totalPages}
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
    </div>
  );
}
