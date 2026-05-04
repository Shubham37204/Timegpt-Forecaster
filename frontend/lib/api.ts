import { ForecastRequest, ForecastResponse } from "@/types/forecast"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function fetchForecast(req: ForecastRequest): Promise<ForecastResponse> {
  try {
    const res = await fetch(`${API_URL}/api/v1/forecast`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(req),
    })

    // Try to parse response safely
    let data: any = null
    try {
      data = await res.json()
    } catch {
      // ignore JSON parse error
    }

    if (!res.ok) {
      // Backend error response
      throw new Error(data?.detail || "Something went wrong")
    }

    return data as ForecastResponse
  } catch (err: any) {
    // Network / fetch failure
    if (err instanceof TypeError) {
      throw new Error("Network error")
    }
    throw err
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/health`)

    if (!res.ok) return false

    const data = await res.json()
    return data?.status === "ok"
  } catch {
    return false
  }
}
