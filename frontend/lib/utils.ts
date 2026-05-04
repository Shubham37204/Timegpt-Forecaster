import { ForecastPoint } from "../types/forecast"
// 1. Format date string for display
// "2026-05-04" → "May 4, 2026"
export function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  })
}

// 2. Format price value
// 247.99 → "$247.99"
export function formatPrice(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value)
}

// 4. Define ChartDataPoint interface
export interface ChartDataPoint {
  date: string
  historical: number | null
  forecast: number | null
  lo_80: number | null
  hi_80: number | null
}

// 3. Merge historical + forecast into single array for chart
export function mergeChartData(
  historical: ForecastPoint[],
  forecast: ForecastPoint[]
): ChartDataPoint[] {
  // Edge case: no historical → only forecast
  if (historical.length === 0) {
    return forecast.map((point) => ({
      date: formatDate(point.date),
      historical: null,
      forecast: point.value,
      lo_80: point.lo_80,
      hi_80: point.hi_80,
    }))
  }

  const lastHistorical = historical[historical.length - 1]

  const historicalData: ChartDataPoint[] = historical.map((point) => ({
    date: formatDate(point.date),
    historical: point.value,
    forecast: null,
    lo_80: null,
    hi_80: null,
  }))

  const forecastData: ChartDataPoint[] = [
    // 🔥 Bridge point (connects lines)
    {
      date: formatDate(lastHistorical.date),
      historical: lastHistorical.value,
      forecast: lastHistorical.value,
      lo_80: null,
      hi_80: null,
    },

    // Forecast points
    ...forecast.map((point) => ({
      date: formatDate(point.date),
      historical: null,
      forecast: point.value,
      lo_80: point.lo_80,
      hi_80: point.hi_80,
    })),
  ]

  return [...historicalData, ...forecastData]
}

export interface MultiTickerPoint {
  date: string
  [ticker: string]: number | null | string
}

export function mergeMultiTickerData(
  results: Record<string, ForecastPoint[]>
): MultiTickerPoint[] {
  const dateSet = new Set<string>()

  // 1. Collect all unique dates
  Object.values(results).forEach((points) => {
    points.forEach((p) => {
      dateSet.add(p.date)
    })
  })

  // 2. Convert to sorted array
  const sortedDates = Array.from(dateSet).sort(
    (a, b) => new Date(a).getTime() - new Date(b).getTime()
  )

  // 3. Build merged structure
  const merged: MultiTickerPoint[] = sortedDates.map((date) => {
    const row: MultiTickerPoint = { date }

    for (const ticker in results) {
      const point = results[ticker].find((p) => p.date === date)
      row[ticker] = point ? point.value : null
    }

    return row
  })

  return merged
}
