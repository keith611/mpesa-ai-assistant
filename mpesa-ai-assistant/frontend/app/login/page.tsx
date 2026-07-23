"use client";

import { useState, FormEvent } from "react";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const { login } = useAuth();
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(phoneNumber, password);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Couldn't sign in. Check your phone number and password.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-sidebar px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="font-display font-bold text-2xl text-white mb-1">M-Pesa AI Assistant</div>
          <div className="text-sidebar-text text-sm">Admin console</div>
        </div>

        <form onSubmit={handleSubmit} className="bg-surface rounded-card border border-border p-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-ink mb-1.5" htmlFor="phone">
              Phone number
            </label>
            <input
              id="phone"
              type="text"
              required
              placeholder="254712345678"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              className="w-full h-10 px-3 rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-brand text-sm"
            />
          </div>
          <div className="mb-5">
            <label className="block text-sm font-medium text-ink mb-1.5" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full h-10 px-3 rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-brand text-sm"
            />
          </div>

          {error && (
            <div className="mb-4 text-sm text-danger-text bg-danger-bg rounded-lg px-3 py-2">{error}</div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full h-10 rounded-lg bg-brand hover:bg-brand-hover text-white text-sm font-medium transition-colors disabled:opacity-60"
          >
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="text-center text-xs text-sidebar-text mt-6">
          Access is limited to Super Admin, Admin, and Support roles.
        </p>
      </div>
    </div>
  );
}
