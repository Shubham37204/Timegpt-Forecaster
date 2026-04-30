import yfinance as yf
import pandas as pd
from typing import Tuple
from app.core.logging import get_logger

log = get_logger(__name__)

MIN_ROWS = 30


class DataFetchError(Exception):
    """Raised when fetched stock data is invalid or insufficient."""
    pass


def fetch_stock_data(ticker: str, period: str) -> Tuple[pd.DataFrame, dict]:
    # 🔹 Download data
    try:
        df = yf.download(
            ticker,
            period=period,
            progress=False,
            auto_adjust=True,
        )
    except Exception as e:
        log.error("yf_download_failed", ticker=ticker, error=str(e))
        raise DataFetchError("Failed to download stock data")

    # 🔹 Empty check
    if df.empty:
        raise DataFetchError("No data returned from yfinance")

    # 🔹 Handle MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # 🔹 Validate Close column
    if "Close" not in df.columns:
        raise DataFetchError("Missing 'Close' column")

    # 🔹 NaN validation
    nan_ratio = df["Close"].isna().mean()
    if nan_ratio > 0.1:
        raise DataFetchError("Too many NaNs in Close prices")

    # 🔹 Drop NaNs
    df = df.dropna(subset=["Close"])

    # 🔹 Minimum rows check
    if len(df) < MIN_ROWS:
        raise DataFetchError(f"Not enough data points (min {MIN_ROWS})")

    # 🔹 Reset index BEFORE rename (important)
    df = df.reset_index()

    # 🔹 Rename columns
    df = df.rename(columns={
        "Date": "ds",
        "Close": "y"
    })

    # 🔹 Add unique_id
    df["unique_id"] = ticker

    # 🔹 Ensure datetime + tz-naive (SAFE VERSION)
    df["ds"] = pd.to_datetime(df["ds"])
    if df["ds"].dt.tz is not None:
        df["ds"] = df["ds"].dt.tz_convert(None)

    # 🔹 Final column order
    df = df[["unique_id", "ds", "y"]]

    # 🔹 Metadata (non-critical)
    meta = {
        "last_price": None,
        "currency": None,
        "company_name": None,
        "rows_fetched": len(df),
    }

    try:
        info = yf.Ticker(ticker).info

        # fallback for missing currentPrice
        meta["last_price"] = (
            info.get("currentPrice")
            or float(df["y"].iloc[-1])
        )
        meta["currency"] = info.get("currency")
        meta["company_name"] = info.get("longName")

    except Exception as e:
        log.warning("metadata_fetch_failed", ticker=ticker, error=str(e))

    return df, meta

# What this file does
# fetch_stock_data.py = data collector + cleaner
