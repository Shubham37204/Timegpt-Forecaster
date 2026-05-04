"use client"

import { useState } from "react"

interface Props {
  onSubmit: (
    tickers: string[],
    horizon: number,
    model: "prophet" | "baseline" | "both"
  ) => void
  loading: boolean
}

export default function ForecastForm({ onSubmit, loading }: Props) {
  const [ticker, setTicker] = useState("")
  const [horizon, setHorizon] = useState(7)
  const [model, setModel] = useState<"prophet" | "baseline" | "both">("both")

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    const tickers = ticker
      .split(",")
      .map((t) => t.trim().toUpperCase())
      .filter((t) => t.length > 0)

    if (tickers.length === 0) return

    onSubmit(tickers, horizon, model)
  }

  const isDisabled = loading || ticker.trim().length === 0

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col md:flex-row gap-4 items-end"
    >
      {/* Ticker Input */}
      <div className="flex flex-col">
        <label className="text-sm font-medium">Tickers</label>
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          placeholder="AAPL, MSFT, GOOGL"
          className="border rounded px-3 py-2"
        />
      </div>

      {/* Horizon Input */}
      <div className="flex flex-col">
        <label className="text-sm font-medium">Horizon</label>
        <input
          type="number"
          min={1}
          value={horizon}
          onChange={(e) => setHorizon(Number(e.target.value))}
          className="border rounded px-3 py-2 w-24"
        />
      </div>

      {/* Model Select */}
      <div className="flex flex-col">
        <label className="text-sm font-medium">Model</label>
        <select
          value={model}
          onChange={(e) =>
            setModel(e.target.value as "prophet" | "baseline" | "both")
          }
          className="border rounded px-3 py-2"
        >
          <option value="both">Both</option>
          <option value="prophet">Prophet</option>
          <option value="baseline">Baseline</option>
        </select>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isDisabled}
        className={`px-4 py-2 rounded text-white ${
          isDisabled
            ? "bg-gray-400 cursor-not-allowed"
            : "bg-blue-600 hover:bg-blue-700"
        }`}
      >
        {loading ? "Loading..." : "Run Forecast"}
      </button>
    </form>
  )
}
