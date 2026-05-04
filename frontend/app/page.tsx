"use client";
import { useState } from "react";
import { ForecastResponse } from "@/types/forecast";
import { fetchForecast } from "@/lib/api";
import { mergeChartData, mergeMultiTickerData } from "@/lib/utils";
import ForecastForm from "@/components/ui/SearchBar";
import StatsCard from "@/components/ui/StatsCard";
import Loader from "@/components/ui/Loader";
import ForecastChart from "@/components/charts/ForecastChart";
import CompareChart from "@/components/charts/CompareChart";
import MultiTickerChart from "@/components/charts/MultiTickerChart";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<ForecastResponse | null>(null);
  const [multiData, setMultiData] = useState<Record<string, ForecastResponse>>(
    {},
  );
  const [tickers, setTickers] = useState<string[]>([]);

  async function handleForecast(
    inputTickers: string[],
    horizon: number,
    model: "prophet" | "baseline" | "both",
  ) {
    setLoading(true);
    setError(null);
    setResponse(null);
    setMultiData({});
    setTickers(inputTickers);

    try {
      const responses = await Promise.all(
        inputTickers.map(async (ticker) => {
          const data = await fetchForecast({
            ticker,
            horizon,
            model,
            use_cache: true,
            period: "6mo",
          });
          return { ticker, data };
        }),
      );

      const resultMap: Record<string, ForecastResponse> = {};
      responses.forEach(({ ticker, data }) => {
        resultMap[ticker] = data;
      });

      setMultiData(resultMap);

      if (inputTickers.length === 1) {
        setResponse(responses[0].data);
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong");
      }
    } finally {
      setLoading(false);
    }
  }

  const prophetResult = response?.results.find(
    (r) => r.model_name === "prophet",
  );
  const lastPrice = response?.historical.at(-1)?.value ?? null;
  const chartData = prophetResult
    ? mergeChartData(response!.historical, prophetResult.forecast)
    : [];

  const multiChartData =
    tickers.length > 1
      ? mergeMultiTickerData(
          Object.fromEntries(
            Object.entries(multiData).map(([ticker, res]) => {
              const prophet = res.results.find(
                (r) => r.model_name === "prophet",
              );
              return [ticker, prophet?.forecast || []];
            }),
          ),
        )
      : [];

  return (
    <main className="max-w-5xl mx-auto px-4 py-8 flex flex-col gap-8">
      <h1 className="text-3xl font-bold">📈 Stock Forecaster</h1>

      <ForecastForm onSubmit={handleForecast} loading={loading} />

      {error && (
        <div className="bg-red-100 text-red-700 px-4 py-3 rounded">{error}</div>
      )}

      {loading && <Loader />}

      {(response || tickers.length > 1) && !loading && (
        <div className="flex flex-col gap-6">
          {tickers.length === 1 && response && (
            <>
              <StatsCard
                ticker={response.ticker}
                lastPrice={lastPrice}
                horizon={response.horizon}
                fromCache={response.from_cache}
                generatedAt={response.generated_at}
              />
              {chartData.length > 0 && (
                <div>
                  <h2 className="text-xl font-semibold mb-2">Forecast</h2>
                  <ForecastChart data={chartData} ticker={response.ticker} />
                </div>
              )}
              {response.results.length > 1 && (
                <div>
                  <h2 className="text-xl font-semibold mb-2">
                    Model Comparison
                  </h2>
                  <CompareChart
                    results={response.results}
                    ticker={response.ticker}
                  />
                </div>
              )}
            </>
          )}

          {tickers.length > 1 && multiChartData.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold mb-2">
                Multi-Ticker Comparison
              </h2>
              <MultiTickerChart data={multiChartData} tickers={tickers} />
            </div>
          )}
        </div>
      )}
    </main>
  );
}
