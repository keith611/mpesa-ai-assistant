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
      setError(null);

      const resp = await api.get<PaginatedUsers>("/users", {
        params: {
          search: search || undefined,
          status: statusFilter || undefined,
          page,
          page_size: pageSize,
        },
      });

      setData(resp.data);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail || "Couldn't load users."
      );
    }
  }, [search, statusFilter, page]);

  useEffect(() => {
    load();
  }, [load]);

  async function toggleStatus(userId: string, current: string) {
    const action = current === "ACTIVE" ? "suspend" : "activate";

    try {
      await api.post(`/users/${userId}/${action}`);
      await load();
    } catch (err: any) {
      alert(
        err?.response?.data?.detail ||
          `Couldn't ${action} user.`
      );
    }
  }

  async function resetPassword(
    userId: string,
    fullName: string
  ) {
    if (
      !confirm(
        `Generate a new temporary password for ${fullName}?\n\nTheir current password will stop working immediately.`
      )
    ) {
      return;
    }

    try {
      const resp = await api.post(
        `/users/${userId}/reset-password"
      );

      alert(
        `New temporary password for ${fullName}:\n\n` +
          `${resp.data.temporary_password}\n\n` +
          `Share this with them through a trusted channel. ` +
          `They should change it after signing in.`
      );
    } catch (err: any) {
      alert(
        err?.response?.data?.detail ||
          "Couldn't reset password."
      );
    }
  }

  async function deleteUser(
    userId: string,
    fullName: string
  ) {
    if (
      !confirm(
        `Are you sure you want to delete ${fullName}?\n\n` +
          `Their account will be marked as deleted.`
      )
    ) {
      return;
    }

    try {
      await api.delete(`/users/${userId}`);
      await load();
    } catch (err: any) {
      alert(
        err?.response?.data?.detail ||
          "Couldn't delete user."
      );
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-ink">
            Users
          </h1>

          <p className="mt-1 text-sm text-ink-secondary">
            Manage Fidika users, accounts and access.
          </p>
        </div>

        {hasMinRole("ADMIN") && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-hover"
          >
            Create user
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <input
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          placeholder="Search users..."
          className="w-full max-w-sm rounded-lg border border-border-subtle bg-white px-3 py-2 text-sm text-ink outline-none focus:border-brand"
        />

        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          className="rounded-lg border border-border-subtle bg-white px-3 py-2 text-sm text-ink outline-none focus:border-brand"
        >
          <option value="">All statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="SUSPENDED">Suspended</option>
          <option value="PENDING">Pending</option>
          <option value="DELETED">Deleted</option>
        </select>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Users table */}
      <div className="overflow-hidden rounded-xl border border-border-subtle bg-white">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-surface-muted text-left text-xs uppercase tracking-wide text-ink-secondary">
                <th className="px-4 py-3 font-medium">
                  User
                </th>

                <th className="px-4 py-3 font-medium">
                  Phone
                </th>

                <th className="px-4 py-3 font-medium">
                  Role
                </th>

                <th className="px-4 py-3 font-medium">
                  Status
                </th>

                <th className="px-4 py-3 font-medium">
                  Registered
                </th>

                <th className="px-4 py-3 font-medium">
                  Last activity
                </th>

                <th className="px-4 py-3 text-right font-medium">
                  Actions
                </th>
              </tr>
            </thead>

            <tbody>
              {data?.users.map((u) => (
                <tr
                  key={u["User ID"]}
                  className="border-t border-border-subtle"
                >
                  {/* User */}
                  <td className="py-2.5 px-4">
                    <Link
                      href={`/users/${u["User ID"]}`}
                      className="flex items-center gap-3 hover:underline"
                    >
                      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand/10 text-xs font-semibold text-brand">
                        {initials(u["Full Name"])}
                      </div>

                      <div>
                        <div className="font-medium text-ink">
                          {u["Full Name"]}
                        </div>

                        <div className="text-xs text-ink-secondary">
                          {u["User ID"]}
                        </div>
                      </div>
                    </Link>
                  </td>

                  {/* Phone */}
                  <td className="px-4 py-2.5 text-ink-secondary">
                    {u["Phone Number"] || "—"}
                  </td>

                  {/* Role */}
                  <td className="px-4 py-2.5">
                    <span className="text-xs font-medium text-ink">
                      {u.Role}
                    </span>
                  </td>

                  {/* Status */}
                  <td className="px-4 py-2.5">
                    <StatusBadge status={u.Status} />
                  </td>

                  {/* Registered */}
                  <td className="px-4 py-2.5 text-ink-secondary">
                    {u["Registration Date"]
                      ? formatDate(u["Registration Date"])
                      : "—"}
                  </td>

                  {/* Last activity */}
                  <td className="px-4 py-2.5 text-ink-secondary">
                    {u["Last Activity"]
                      ? formatDate(u["Last Activity"])
                      : "—"}
                  </td>

                  {/* Actions */}
                  <td className="py-2.5 px-4 text-right space-x-3">
                    {/* Admin actions */}
                    {hasMinRole("ADMIN") &&
                      u.Status !== "DELETED" && (
                        <>
                          <button
                            onClick={() =>
                              resetPassword(
                                u["User ID"],
                                u["Full Name"]
                              )
                            }
                            className="text-xs font-medium text-ink-secondary hover:text-ink"
                          >
                            Reset password
                          </button>

                          <button
                            onClick={() =>
                              toggleStatus(
                                u["User ID"],
                                u.Status
                              )
                            }
                            className="text-xs font-medium text-brand hover:text-brand-hover"
                          >
                            {u.Status === "ACTIVE"
                              ? "Suspend"
                              : "Activate"}
                          </button>
                        </>
                      )}

                    {/* Super Admin delete action */}
                    {hasMinRole("SUPER_ADMIN") &&
                      u.Status !== "DELETED" && (
                        <button
                          onClick={() =>
                            deleteUser(
                              u["User ID"],
                              u["Full Name"]
                            )
                          }
                          className="text-xs font-medium text-danger-text hover:underline"
                        >
                          Delete
                        </button>
                      )}
                  </td>
                </tr>
              ))}

              {/* Empty state */}
              {data?.users?.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 py-10 text-center text-sm text-ink-secondary"
                  >
                    No users found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data && (
          <div className="flex items-center justify-between border-t border-border-subtle px-4 py-3">
            <div className="text-xs text-ink-secondary">
              Page {page}
              {data.total != null &&
                ` · ${data.total} users`}
            </div>

            <div className="flex gap-2">
              <button
                disabled={page <= 1}
                onClick={() =>
                  setPage((p) => Math.max(1, p - 1))
                }
                className="rounded-lg border border-border-subtle px-3 py-1.5 text-xs font-medium text-ink disabled:cursor-not-allowed disabled:opacity-40"
              >
                Previous
              </button>

              <button
                disabled={
                  !data.users ||
                  data.users.length < pageSize
                }
                onClick={() =>
                  setPage((p) => p + 1)
                }
                className="rounded-lg border border-border-subtle px-3 py-1.5 text-xs font-medium text-ink disabled:cursor-not-allowed disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Create user modal */}
      {showCreateModal && (
        <CreateUserModal
          onClose={() => setShowCreateModal(false)}
          onCreated={async () => {
            setShowCreateModal(false);
            await load();
          }}
        />
      )}
    </div>
  );
}
