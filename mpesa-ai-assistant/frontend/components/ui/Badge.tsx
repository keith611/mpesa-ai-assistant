import { statusColor, categoryColor } from "@/lib/utils";

export function StatusBadge({ status }: { status: string }) {
  const c = statusColor(status);
  return (
    <span className={`badge ${c.bg} ${c.text}`}>
      <span className={`status-dot ${c.dot} mr-1.5`} />
      {status}
    </span>
  );
}

export function CategoryBadge({ category }: { category: string }) {
  const c = categoryColor(category);
  return <span className={`badge ${c.bg} ${c.text}`}>{category}</span>;
}
