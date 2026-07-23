"use client";

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

interface Props {
  data: { date: string; new_users: number }[];
}

export default function UserGrowthChart({ data }: Props) {
  if (data.length === 0) {
    return <div className="text-sm text-ink-secondary flex items-center justify-center h-64">No new users in this period.</div>;
  }
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#EDF1EE" vertical={false} />
        <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#5E6E68" }} axisLine={{ stroke: "#E2E8E5" }} tickLine={false} />
        <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#5E6E68" }} axisLine={false} tickLine={false} width={30} />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
        <Line type="monotone" dataKey="new_users" name="New users" stroke="#0F6659" strokeWidth={2} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
