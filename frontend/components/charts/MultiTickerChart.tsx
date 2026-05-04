"use client"

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"

import { MultiTickerPoint } from "@/lib/utils"

interface Props {
  data: MultiTickerPoint[]
  tickers: string[]
}

const COLORS = ["#2563eb", "#f97316", "#10b981", "#8b5cf6", "#ef4444"]

export default function MultiTickerChart({ data, tickers }: Props) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />

        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />

        {tickers.map((ticker, index) => (
          <Line
            key={ticker}
            type="monotone"
            dataKey={ticker} // 🔥 dynamic key
            stroke={COLORS[index % COLORS.length]} // cycle colors
            strokeWidth={2}
            dot={false}
            connectNulls={true}
            name={ticker}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
