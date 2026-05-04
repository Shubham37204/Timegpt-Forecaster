import { ModelResult } from "@/types/forecast"
import {
  LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts"

const MODEL_COLORS: Record<string, string> = {
  baseline_arima_ets: "#10b981",
  prophet: "#8b5cf6",
}

interface Props {
  results: ModelResult[]
  ticker: string
}


export function mergeModelForecasts(results: ModelResult[]) {
  const map = new Map<string, any>()

  results.forEach((model) => {
    model.forecast.forEach((point) => {
      const date = point.date

      if (!map.has(date)) {
        map.set(date, { date })
      }

      map.get(date)[model.model_name] = point.value
    })
  })

  return Array.from(map.values()).sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  )
}

export default function CompareChart({ results, ticker }: Props) {
  const data = mergeModelForecasts(results)

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        {results.map((model) => (
          <Line
            key={model.model_name}
            type="monotone"
            dataKey={model.model_name}
            stroke={MODEL_COLORS[model.model_name] ?? "#6b7280"}
            strokeWidth={2}
            dot={false}
            connectNulls={true}
            name={model.model_name}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}