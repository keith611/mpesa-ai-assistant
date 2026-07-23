"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { formatMoney } from "@/lib/utils";

const COLORS = ["#0F6659", "#2F9E6E", "#E3A23D", "#C1483B", "#5DCAA5", "#7F77DD", "#D85A30", "#378ADD", "#993C1D", "#639922"];

interface Props {
  data: { category: string; amount: number }[];
}

export default function CategoryPieChart({ data }: Props) {
  if (data.length === 0) {
    return <div className="text-sm text-ink-secondary flex items-center justify-center h-64">No category data yet.</div>;
  }
  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={data}
          dataKey="amount"
          nameKey="category"
          cx="50%"
          cy="50%"
          innerRadius={55}
          outerRadius={95}
          paddingAngle={2}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} stroke="none" />
          ))}
        </Pie>
        <Tooltip formatter={(value: number) => formatMoney(value)} contentStyle={{ fontSize: 12, borderRadius: 8 }} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
      </PieChart>
    </ResponsiveContainer>
  );
}
