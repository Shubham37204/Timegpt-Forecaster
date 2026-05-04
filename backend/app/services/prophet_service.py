from prophet import Prophet
import pandas as pd
from typing import List

from app.core.logging import get_logger
from app.models.forecast import ForecastPoint, ModelResult

log = get_logger(__name__)


def run_prophet(df: pd.DataFrame, horizon: int) -> ModelResult:
    try:
        # 1️⃣ Keep only required columns
        pdf = df[["ds", "y"]].copy()

        # Ensure correct dtypes
        pdf["ds"] = pd.to_datetime(pdf["ds"])
        pdf["y"] = pd.to_numeric(pdf["y"], errors="coerce")

        # Drop any bad rows
        pdf = pdf.dropna(subset=["ds", "y"])

        if len(pdf) < 10:
            raise ValueError("Not enough data for Prophet")

        # 2️⃣ Init & fit
        model = Prophet(
            interval_width=0.80,   # matches your lo_80 / hi_80
            daily_seasonality=False
        )
        model.fit(pdf)

        # 3️⃣ Future dataframe (business days)
        future = model.make_future_dataframe(periods=horizon, freq="B")

        # 4️⃣ Predict
        forecast = model.predict(future)

        # 5️⃣ Take only future horizon rows
        forecast_future = forecast.tail(horizon)

        # 6️⃣ Build ForecastPoint list
        points: List[ForecastPoint] = []

        for _, row in forecast_future.iterrows():
            points.append(
                ForecastPoint(
                    date=str(row["ds"])[:10],
                    value=round(float(row["yhat"]), 2),
                    lo_80=round(float(row["yhat_lower"]), 2),
                    hi_80=round(float(row["yhat_upper"]), 2),
                )
            )

        return ModelResult(
            model_name="prophet",
            forecast=points,
            mae=None,
            mape=None,
        )

    except Exception as e:
        log.error("prophet_failed", error=str(e))

        raise RuntimeError(f"Prophet failed: {e}") from e


# What this file does (simple)
# run_prophet = smarter forecasting model (trend + seasonality)
