from typing import List, Optional
import pandas as pd
from nixtla import NixtlaClient
from app.core.config import settings
from app.core.logging import get_logger
from app.models.forecast import ForecastPoint, ModelResult

log = get_logger(__name__)

_client: Optional[NixtlaClient] = None  # lazy singleton


def _get_client() -> NixtlaClient:
    global _client
    if _client is not None:
        return _client

    # create once (may perform network/auth checks)
    _client = NixtlaClient(api_key=settings.nixtla_api_key)
    return _client


def run_timegpt(df: pd.DataFrame, horizon: int) -> ModelResult:
    ticker = str(df["unique_id"].iloc[0])

    try:
        client = _get_client()

        fcst = client.forecast(
            df=df,
            h=horizon,
            freq="B",
            level=[80],
            time_col="ds",
            target_col="y",
            id_col="unique_id",
        )

        # Some versions return index with ds; ensure column
        if "ds" not in fcst.columns:
            fcst = fcst.reset_index()

        cols = fcst.columns.tolist()

        # 🔍 dynamic detection (robust to version changes)
        point_cols = [
            c for c in cols
            if "TimeGPT" in c and "lo" not in c and "hi" not in c
        ]
        lo_cols = [c for c in cols if "TimeGPT" in c and "lo" in c and "80" in c]
        hi_cols = [c for c in cols if "TimeGPT" in c and "hi" in c and "80" in c]

        if not point_cols:
            raise RuntimeError("No TimeGPT forecast column found")

        point_col = point_cols[0]
        lo_col = lo_cols[0] if lo_cols else None
        hi_col = hi_cols[0] if hi_cols else None

        points: List[ForecastPoint] = []

        for _, row in fcst.iterrows():
            # date as YYYY-MM-DD
            date_str = str(row["ds"])[:10]

            points.append(
                ForecastPoint(
                    date=date_str,
                    value=float(row[point_col]),
                    lo_80=float(row[lo_col]) if lo_col else None,
                    hi_80=float(row[hi_col]) if hi_col else None,
                )
            )

        return ModelResult(
            model_name="timegpt-1",
            forecast=points,
            mae=None,
            mape=None,
        )

    except Exception as e:
        # DO NOT swallow — escalate to orchestrator
        log.error("timegpt_failed", ticker=ticker, error=str(e))
        raise RuntimeError(f"TimeGPT failed for {ticker}") from e


def validate_api_key() -> bool:
    try:
        client = _get_client()
        return bool(client.validate_api_key())
    except Exception as e:
        log.warning("nixtla_key_invalid_or_unreachable", error=str(e))
        return False

# What this file does
# timegpt.py = AI forecasting adapter