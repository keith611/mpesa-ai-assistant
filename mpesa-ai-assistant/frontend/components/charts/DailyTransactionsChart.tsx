"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

interface Props {
  data: { date: string; transaction_count: number }[];
}

export default function DailyTransactionsChart({ data }: Props) {
  if (data.length === 0) {
    return <div className="text-sm text-ink-secondary flex items-center justify-center h-64">No transactions in this period.</div>;
  }
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#EDF1EE" vertical={false} />
        <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#5E6E68" }} axisLine={{ stroke: "#E2E8E5" }} tickLine={false} />
        <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#5E6E68" }} axisLine={false} tickLine={false} width={30} />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
        <Bar dataKey="transaction_count" name="Transactions" fill="#0F6659" radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
