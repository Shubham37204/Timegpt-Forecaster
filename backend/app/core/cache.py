import diskcache
import hashlib
from typing import Any, Optional
from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)
_cache = diskcache.Cache(settings.cache_dir)

def _make_key(ticker: str, horizon: int, period: str) -> str:
    raw = f"{ticker.upper()}:{horizon}:{period}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def get_cached(ticker: str, horizon: int, period: str) -> Optional[dict]:
    key = _make_key(ticker, horizon, period)

    result = _cache.get(key)

    if result is not None:
        log.info("cache_hit", key=key, ticker=ticker)
        return result

    log.info("cache_miss", key=key, ticker=ticker)
    return None


def set_cached(ticker: str, horizon: int, period: str, data: Any) -> None:
    key = _make_key(ticker, horizon, period)

    _cache.set(
        key,
        data,
        expire=settings.cache_ttl_seconds
    )

    log.info(
        "cache_set",
        key=key,
        ticker=ticker,
        ttl=settings.cache_ttl_seconds
    )
    

#what does this files do??

# Think of this like a dumb storage box
# It only stores and returns data
# It doesn’t care what the data means

# "I give you data → you store it"
# "I ask for data → you return it"

# ❗ It DOES NOT know:
# what a forecast is
# what Pydantic is
# what your app logic is
