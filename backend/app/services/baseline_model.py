import pandas as pd
import numpy as np
from typing import List, Optional
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, AutoETS
from app.core.logging import get_logger
from app.models.forecast import ForecastPoint, ModelResult

log = get_logger(__name__)


def run_baseline(df: pd.DataFrame, horizon: int) -> ModelResult:
    try:
        # 1. Initialize models
        models = [
            AutoARIMA(),
            AutoETS()
        ]

        sf = StatsForecast(
            models=models,
            freq="B",   # business day frequency
            n_jobs=1
        )

        # 2. Fit and predict
        sf.fit(df)
        fcst = sf.predict(h=horizon, level=[80])

        # 3. Reset index
        fcst = fcst.reset_index()

        # 🔍 Dynamic column detection
        cols = fcst.columns.tolist()

        # point forecasts (no lo/hi)
        point_cols = [
            c for c in cols
            if ("ARIMA" in c or "ETS" in c)
            and "lo" not in c
            and "hi" not in c
        ]

        # confidence intervals
        lo_cols = [c for c in cols if "lo" in c and "80" in c]
        hi_cols = [c for c in cols if "hi" in c and "80" in c]

        # 4. Ensemble average
        if point_cols:
            fcst["ensemble"] = fcst[point_cols].mean(axis=1)
        else:
            log.warning("no_point_forecast_columns_found")
            return ModelResult(
                model_name="baseline_arima_ets",
                forecast=[],
                mae=None,
                mape=None
            )

        # 5. Extract intervals (use first available)
        lo_col = lo_cols[0] if lo_cols else None
        hi_col = hi_cols[0] if hi_cols else None

        # 6. Build ForecastPoint list
        forecast_points: List[ForecastPoint] = []

        for _, row in fcst.iterrows():
            forecast_points.append(
                ForecastPoint(
                    date=str(row["ds"])[:10],
                    value=float(row["ensemble"]),
                    lo_80=float(row[lo_col]) if lo_col else None,
                    hi_80=float(row[hi_col]) if hi_col else None,
                )
            )

        # 7. Compute MAE
        mae = _quick_mae(df, horizon)

        # 8. Return result
        return ModelResult(
            model_name="baseline_arima_ets",
            forecast=forecast_points,
            mae=mae,
            mape=None
        )

    except Exception as e:
        log.error("baseline_failed", error=str(e))

        return ModelResult(
            model_name="baseline_arima_ets",
            forecast=[],
            mae=None,
            mape=None
        )


def _quick_mae(df: pd.DataFrame, horizon: int) -> Optional[float]:
    try:
        # 1. Not enough data
        if len(df) < horizon * 2:
            return None

        # 2. Split
        train = df.iloc[:-horizon]
        actual = df["y"].iloc[-horizon:].values

        # 3. Naive forecast
        last_value = train["y"].iloc[-1]
        naive = np.full(horizon, last_value)

        # 4. MAE
        mae = np.mean(np.abs(actual - naive))

        return float(mae)

    except Exception as e:
        log.warning("mae_failed", error=str(e))
        return None
    
#What this file does
#baseline.py = “cheap, reliable forecaster”