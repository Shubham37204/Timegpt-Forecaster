from datetime import datetime, timezone
from typing import List
from app.core import cache as cache_store
from app.core.logging import get_logger
from app.models.forecast import (
    ForecastRequest,
    ForecastResponse,
    ForecastPoint,
    ModelResult,
)
from app.services.data_fetcher import fetch_stock_data, DataFetchError
from app.services.prophet_service import run_prophet
from app.services.baseline_model import run_baseline

log = get_logger(__name__)


async def run_forecast(req: ForecastRequest) -> ForecastResponse:

    # 1. Cache check
    if req.use_cache:
        cached = cache_store.get_cached(req.ticker, req.horizon, req.period)
        if cached is not None:
            log.info("cache_returned", ticker=req.ticker)
            return ForecastResponse(**{**cached, "from_cache": True})

    # 2. Fetch data
    df, meta = fetch_stock_data(req.ticker, req.period)

    # 3. Build historical (last 30 rows)
    historical: List[ForecastPoint] = [
        ForecastPoint(date=str(row["ds"])[:10],
                      value=round(float(row["y"]), 2))
        for _, row in df.tail(30).iterrows()
    ]

    # 4. Run models
    results: List[ModelResult] = []

    if req.model in ("baseline", "both"):
        baseline_res = run_baseline(df, req.horizon)
        results.append(baseline_res)

    if req.model in ("prophet", "both"):
        try:
            prophet_res = run_prophet(df, req.horizon)
            results.append(prophet_res)
        except RuntimeError as e:
            log.warning("prophet_failed_fallback", error=str(e))
            results.append(ModelResult(
                model_name="prophet",
                forecast=[],
                mae=None,
                mape=None,
            ))

    # 5. Build response
    response = ForecastResponse(
        ticker=req.ticker,
        generated_at=datetime.now(timezone.utc).isoformat(),
        period_used=req.period,
        horizon=req.horizon,
        historical=historical,
        results=results,
        from_cache=False,
    )

    # 6. Cache store
    if req.use_cache and any(r.forecast for r in results):
        cache_store.set_cached(
            req.ticker,
            req.horizon,
            req.period,
            response.model_dump(),
        )

    # 7. Return
    return response

# What this file does
# forecaster.py = takes a request → runs everything → returns final result
# forecaster.py = orchestrator that connects cache + data + models and produces final output
