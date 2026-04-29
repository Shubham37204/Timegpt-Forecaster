from nixtla import NixtlaClient
import yfinance as yf
import pandas as pd

client = NixtlaClient(api_key="your_key")

df = yf.download("AAPL", period="6mo")["Close"].reset_index()
df.columns = ["ds", "y"]
df["unique_id"] = "AAPL"

# Fix time series
df = df.set_index("ds").asfreq("B")
df["y"] = df["y"].ffill()
df["unique_id"] = df["unique_id"].ffill()  # 🔥 important fix
df = df.reset_index()

forecast = client.forecast(df, h=7, freq="B")

print(forecast)