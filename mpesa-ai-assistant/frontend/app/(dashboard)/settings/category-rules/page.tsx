"use client";

import { useEffect, useState, FormEvent } from "react";
import { api } from "@/lib/api";
import { CategoryRule } from "@/lib/types";

const CATEGORIES = [
  "Food", "Transport", "Fuel", "Rent", "Utilities", "Business",
  "Shopping", "Entertainment", "Education", "Healthcare", "Other",
];

export default function CategoryRulesPage() {
  const [rules, setRules] = useState<CategoryRule[]>([]);
  const [keyword, setKeyword] = useState("");
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [priority, setPriority] = useState(5);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      const resp = await api.get<CategoryRule[]>("/admin/category-rules");
      setRules(resp.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Couldn't load category rules.");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function addRule(e: FormEvent) {
    e.preventDefault();
    if (!keyword.trim()) return;
    try {
      await api.post("/admin/category-rules", { keyword, category, priority });
      setKeyword("");
      load();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Couldn't add rule.");
    }
  }

  async function toggleActive(rule: CategoryRule) {
    try {
      await api.patch(`/admin/category-rules/${rule["Rule ID"]}`, { Active: !rule.Active });
      load();
    } catch {
      setError("Couldn't update rule.");
    }
  }

  async function deleteRule(ruleId: string) {
    if (!confirm("Delete this category rule?")) return;
    try {
      await api.delete(`/admin/category-rules/${ruleId}`);
      load();
    } catch {
      setError("Couldn't delete rule.");
    }
  }

  return (
    <div className="space-y-5">
      <div className="card">
        <div className="font-display font-semibold text-[13px] mb-1">Add a category rule</div>
        <p className="text-sm text-ink-secondary mb-3">
          Transactions are categorized automatically when the keyword appears in the sender, receiver, or account
          reference. Higher priority rules are checked first.
        </p>
        <form onSubmit={addRule} className="flex items-end gap-3">
          <div className="flex-1">
            <label className="block text-xs font-medium text-ink-secondary mb-1">Keyword</label>
            <input
              type="text"
              placeholder="e.g. NAIVAS"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              className="w-full h-9 px-3 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-brand/30"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-ink-secondary mb-1">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="h-9 px-3 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-brand/30"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-ink-secondary mb-1">Priority</label>
            <input
              type="number"
              min={1}
              max={20}
              value={priority}
              onChange={(e) => setPriority(Number(e.target.value))}
              className="w-20 h-9 px-3 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-brand/30"
            />
          </div>
          <button
            type="submit"
            className="h-9 px-4 rounded-lg bg-brand hover:bg-brand-hover text-white text-sm font-medium"
          >
            Add rule
          </button>
        </form>
      </div>

      {error && <div className="text-sm text-danger-text bg-danger-bg rounded-lg px-4 py-3">{error}</div>}

      <div className="card !p-0 overflow-hidden">
        <table className="w-full text-[13px]">
          <thead>
            <tr className="text-left text-ink-secondary text-xs bg-canvas">
              <th className="font-medium py-2.5 px-4">Keyword</th>
              <th className="font-medium py-2.5 px-4">Category</th>
              <th className="font-medium py-2.5 px-4">Priority</th>
              <th className="font-medium py-2.5 px-4">Active</th>
              <th className="font-medium py-2.5 px-4">Updated by</th>
              <th className="font-medium py-2.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rules
              .slice()
              .sort((a, b) => b.Priority - a.Priority)
              .map((r) => (
                <tr key={r["Rule ID"]} className="border-t border-border-subtle">
                  <td className="py-2.5 px-4 table-figure text-ink">{r.Keyword}</td>
                  <td className="py-2.5 px-4 text-ink-secondary">{r.Category}</td>
                  <td className="py-2.5 px-4 table-figure text-ink-secondary">{r.Priority}</td>
                  <td className="py-2.5 px-4">
                    <span className={`badge ${r.Active ? "bg-success-bg text-success-text" : "bg-canvas text-ink-secondary"}`}>
                      {r.Active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-ink-secondary">{r["Updated By"]}</td>
                  <td className="py-2.5 px-4 text-right space-x-3">
                    <button onClick={() => toggleActive(r)} className="text-xs font-medium text-brand hover:text-brand-hover">
                      {r.Active ? "Deactivate" : "Activate"}
                    </button>
                    <button onClick={() => deleteRule(r["Rule ID"])} className="text-xs font-medium text-danger-text hover:opacity-80">
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            {rules.length === 0 && (
              <tr>
                <td colSpan={6} className="py-8 text-center text-ink-secondary">
                  No category rules yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
