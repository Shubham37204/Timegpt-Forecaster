export interface ForecastPoint {
  date: string
  value: number
  lo_80: number | null
  hi_80: number | null
}

export interface ModelResult {
  model_name: string
  forecast: ForecastPoint[]
  mae: number | null
  mape: number | null
}

export interface ForecastResponse {
  ticker: string
  generated_at: string
  period_used: string
  horizon: number
  historical: ForecastPoint[]
  results: ModelResult[]
  from_cache: boolean
}

export interface ForecastRequest {
  ticker: string              // e.g. "AAPL", "BTC-USD"
  horizon: number             // number of future points to forecast
  period?: "1mo" | "3mo" | "6mo" | "1y" | "2y"           // e.g. "1y", "6mo", "max"
  use_cache?: boolean         // whether to use cached results
  model?: "prophet" | "baseline" | "both"    // specific model (e.g. "arima", "prophet", "lstm")
}

export interface ErrorResponse {
  detail: string
}
