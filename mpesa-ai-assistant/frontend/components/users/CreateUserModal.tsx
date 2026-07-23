"use client";

import { useState, FormEvent } from "react";
import { api } from "@/lib/api";

interface Props {
  onClose: () => void;
  onCreated: () => void;
}

const ROLES = ["USER", "SUPPORT", "ADMIN", "SUPER_ADMIN"];

export default function CreateUserModal({ onClose, onCreated }: Props) {
  const [fullName, setFullName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [whatsappNumber, setWhatsappNumber] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("USER");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!fullName || !phoneNumber || !password) {
      setError("Full name, phone number, and password are required.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setSubmitting(true);
    try {
      await api.post("/users", null, {
        params: {
          full_name: fullName,
          phone_number: phoneNumber,
          whatsapp_number: whatsappNumber || phoneNumber,
          password,
          role,
        },
      });
      onCreated();
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Couldn't create user. The phone number may already be registered.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-card border border-border w-full max-w-md p-6">
        <div className="font-display font-semibold text-[15px] mb-1">Create user</div>
        <p className="text-sm text-ink-secondary mb-4">
          Creates an account directly — useful for onboarding someone without them self-registering.
        </p>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-ink-secondary mb-1">Full name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full h-9 px-3 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-brand/30"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-ink-secondary mb-1">Phone number</label>
            <input
              type="text"
              placeholder="254712345678"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              className="w-full h-9 px-3 rounded-lg border border-border text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand/30"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-ink-secondary mb-1">WhatsApp number (optional — defaults to phone number)</label>
            <input
              type="text"
              placeholder="254712345678"
              value={whatsappNumber}
              onChange={(e) => setWhatsappNumber(e.target.value)}
              className="w-full h-9 px-3 rounded-lg border border-border text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand/30"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-ink-secondary mb-1">Temporary password (min 8 characters)</label>
            <input
              type="text"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full h-9 px-3 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-brand/30"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-ink-secondary mb-1">Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full h-9 px-3 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-brand/30"
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          {error && <div className="text-sm text-danger-text bg-danger-bg rounded-lg px-3 py-2">{error}</div>}

          <div className="flex gap-2 pt-2">
            <button
              type="submit"
              disabled={submitting}
              className="h-9 px-4 rounded-lg bg-brand hover:bg-brand-hover text-white text-sm font-medium disabled:opacity-60"
            >
              {submitting ? "Creating…" : "Create user"}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="h-9 px-4 rounded-lg border border-border text-sm font-medium hover:bg-canvas"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
