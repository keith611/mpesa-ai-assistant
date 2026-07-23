"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { api, setTokens, clearTokens } from "./api";
import { AppUser, Role } from "./types";

interface AuthContextValue {
  user: AppUser | null;
  loading: boolean;
  login: (phoneNumber: string, password: string) => Promise<void>;
  logout: () => void;
  hasMinRole: (role: Role) => boolean;
}

const ROLE_RANK: Record<Role, number> = { SUPER_ADMIN: 4, ADMIN: 3, SUPPORT: 2, USER: 1 };

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AppUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  async function fetchProfile() {
    try {
      const resp = await api.get<AppUser>("/users/me");
      setUser(resp.data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("mpesa_access_token") : null;
    if (token) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, []);

  async function login(phoneNumber: string, password: string) {
    const resp = await api.post("/auth/login", { phone_number: phoneNumber, password });
    setTokens(resp.data.access_token, resp.data.refresh_token);
    await fetchProfile();
    router.push("/overview");
  }

  function logout() {
    clearTokens();
    setUser(null);
    router.push("/login");
  }

  function hasMinRole(role: Role): boolean {
    if (!user) return false;
    return ROLE_RANK[user.Role] >= ROLE_RANK[role];
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, hasMinRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
