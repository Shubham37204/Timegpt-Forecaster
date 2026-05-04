import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { ChartDataPoint } from "@/lib/utils";

interface Props {
  data: ChartDataPoint[];
  ticker: string;
}

export default function ForecastChart({ data, ticker }: Props) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <ComposedChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />

        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />

        {/* 🔵 1. Confidence band (hi - lo) */}
        {/* Base (lo_80) — invisible but needed for stacking */}
        <Area
          type="monotone"
          dataKey="lo_80"
          stroke="none"
          fill="white"
          connectNulls={true}
        />

        {/* Top (hi_80) — visible shaded band */}
        <Area
          type="monotone"
          dataKey="hi_80"
          stroke="none"
          fill="#f97316"
          fillOpacity={0.2}
        />

        {/* 🔵 2. Historical line */}
        <Line
          type="monotone"
          dataKey="historical"
          stroke="#2563eb"
          strokeWidth={2}
          dot={false}
          connectNulls={true}
          name={`${ticker} (Historical)`}
        />

        {/* 🟠 3. Forecast line */}
        <Line
          type="monotone"
          dataKey="forecast"
          stroke="#f97316"
          strokeWidth={2}
          strokeDasharray="5 5"
          dot={false}
          connectNulls={true}
          name={`${ticker} (Forecast)`}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
