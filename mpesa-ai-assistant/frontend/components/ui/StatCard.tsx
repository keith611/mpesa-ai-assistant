interface StatCardProps {
  label: string;
  value: string;
  tone?: "default" | "positive" | "negative";
}

export default function StatCard({ label, value, tone = "default" }: StatCardProps) {
  const toneClass = tone === "positive" ? "text-brand" : tone === "negative" ? "text-danger" : "text-ink";
  return (
    <div className="card">
      <div className="text-xs text-ink-secondary mb-1.5">{label}</div>
      <div className={`font-mono text-[22px] font-medium ${toneClass}`}>{value}</div>
    </div>
  );
}
