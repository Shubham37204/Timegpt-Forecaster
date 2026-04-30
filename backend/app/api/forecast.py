from fastapi import APIRouter, HTTPException
from app.models.forecast import ForecastRequest, ForecastResponse
from app.services.forecaster import run_forecast
from app.services.data_fetcher import DataFetchError
from app.core.logging import get_logger

router = APIRouter()
log = get_logger(__name__)


@router.post("/forecast", response_model=ForecastResponse)
async def forecast_endpoint(req: ForecastRequest):
    try:
        # 1. Run pipeline
        result = await run_forecast(req)
        return result

    except DataFetchError as e:
        # 2. User error (bad ticker / insufficient data)
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )

    except Exception as e:
        # 3. Internal error
        log.error("forecast_failed", error=str(e), ticker=req.ticker)

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

# What this file does (simple)
# forecast endpoint = bridge between user request and your system