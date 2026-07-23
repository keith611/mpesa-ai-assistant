export function formatMoney(amount: number | null | undefined): string {
  const value = typeof amount === "number" && !isNaN(amount) ? amount : 0;
  return `KES ${value.toLocaleString("en-KE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function formatCompactMoney(amount: number | null | undefined): string {
  const value = typeof amount === "number" && !isNaN(amount) ? amount : 0;
  if (Math.abs(value) >= 1_000_000) return `KES ${(value / 1_000_000).toFixed(1)}M`;
  if (Math.abs(value) >= 1_000) return `KES ${(value / 1_000).toFixed(1)}K`;
  return formatMoney(value);
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleDateString("en-KE", { year: "numeric", month: "short", day: "numeric" });
  } catch {
    return iso;
  }
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("en-KE", { year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  } catch {
    return iso;
  }
}

export function initials(name: string | null | undefined): string {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export function statusColor(status: string): { dot: string; bg: string; text: string } {
  switch (status) {
    case "ACTIVE":
      return { dot: "bg-success", bg: "bg-success-bg", text: "text-success-text" };
    case "SUSPENDED":
      return { dot: "bg-danger", bg: "bg-danger-bg", text: "text-danger-text" };
    case "PENDING":
      return { dot: "bg-warning", bg: "bg-warning-bg", text: "text-warning-text" };
    default:
      return { dot: "bg-ink-muted", bg: "bg-canvas", text: "text-ink-secondary" };
  }
}

export function categoryColor(category: string): { bg: string; text: string } {
  const map: Record<string, { bg: string; text: string }> = {
    Food: { bg: "bg-success-bg", text: "text-success-text" },
    Shopping: { bg: "bg-brand-50", text: "text-brand-800" },
    Fuel: { bg: "bg-danger-bg", text: "text-danger-text" },
    Transport: { bg: "bg-warning-bg", text: "text-warning-text" },
    Rent: { bg: "bg-brand-50", text: "text-brand-800" },
    Utilities: { bg: "bg-warning-bg", text: "text-warning-text" },
    Business: { bg: "bg-success-bg", text: "text-success-text" },
    Entertainment: { bg: "bg-danger-bg", text: "text-danger-text" },
    Education: { bg: "bg-brand-50", text: "text-brand-800" },
    Healthcare: { bg: "bg-success-bg", text: "text-success-text" },
  };
  return map[category] || { bg: "bg-canvas", text: "text-ink-secondary" };
}
