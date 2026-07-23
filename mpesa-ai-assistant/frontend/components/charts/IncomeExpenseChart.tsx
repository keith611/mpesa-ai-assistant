"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import { formatCompactMoney, formatMoney } from "@/lib/utils";

interface Props {
  data: { month: string; income: number; expense: number }[];
}

export default function IncomeExpenseChart({ data }: Props) {
  if (data.length === 0) {
    return <div className="text-sm text-ink-secondary flex items-center justify-center h-64">No monthly history yet.</div>;
  }
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#EDF1EE" vertical={false} />
        <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#5E6E68" }} axisLine={{ stroke: "#E2E8E5" }} tickLine={false} />
        <YAxis
          tickFormatter={(v) => formatCompactMoney(v)}
          tick={{ fontSize: 11, fill: "#5E6E68" }}
          axisLine={false}
          tickLine={false}
          width={70}
        />
        <Tooltip formatter={(value: number) => formatMoney(value)} contentStyle={{ fontSize: 12, borderRadius: 8 }} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey="income" name="Income" fill="#0F6659" radius={[3, 3, 0, 0]} />
        <Bar dataKey="expense" name="Expense" fill="#C1483B" radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
