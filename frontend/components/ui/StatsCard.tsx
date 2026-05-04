import { formatPrice, formatDate } from "@/lib/utils"

interface Props {
  ticker: string
  lastPrice: number | null
  horizon: number
  fromCache: boolean
  generatedAt: string
}

export default function ForecastSummary({
  ticker,
  lastPrice,
  horizon,
  fromCache,
  generatedAt,
}: Props) {
  return (
    <div className="border rounded-xl p-4 shadow-sm flex flex-col gap-2">
      
      {/* 🔥 Ticker */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">{ticker}</h2>

        {/* Cache Badge */}
        <span
          className={`text-xs px-2 py-1 rounded-full font-medium ${
            fromCache
              ? "bg-yellow-100 text-yellow-700"
              : "bg-green-100 text-green-700"
          }`}
        >
          {fromCache ? "Cached" : "Live"}
        </span>
      </div>

      {/* 💰 Last Price */}
      <div className="text-lg">
        Last Price:{" "}
        <span className="font-semibold">
          {lastPrice !== null ? formatPrice(lastPrice) : "-"}
        </span>
      </div>

      {/* 📈 Horizon */}
      <div className="text-sm text-gray-600">
        {horizon} {horizon === 1 ? "day" : "days"} ahead
      </div>

      {/* 🕒 Generated Time */}
      <div className="text-xs text-gray-500">
        Generated: {formatDate(generatedAt)}
      </div>
    </div>
  )
}
