from pydantic import BaseModel, field_validator, Field
from typing import List, Literal, Optional
import re

class ForecastRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    horizon: int = Field(default=7, ge=1, le=90)
    period: Literal["1mo", "3mo", "6mo", "1y", "2y"] = "6mo"
    use_cache: bool = True
    model: Literal["prophet", "baseline", "both"] = "both"

    @field_validator("ticker")
    @classmethod
    def normalise_ticker(cls, v: str) -> str:
        v = v.strip().upper()
        if not re.match(r"^[A-Z0-9.\-]+$", v):
            raise ValueError("Invalid ticker format")
        return v

class ForecastPoint(BaseModel):
    date: str  
    value: float
    lo_80: Optional[float] = None
    hi_80: Optional[float] = None

class ModelResult(BaseModel):
    model_config = {"protected_namespaces": ()}  
    model_name: str
    forecast: List[ForecastPoint]
    mae: Optional[float] = None
    mape: Optional[float] = None

class ForecastResponse(BaseModel):
    ticker: str
    generated_at: str
    period_used: str
    horizon: int
    historical: List[ForecastPoint]
    results: List[ModelResult]
    from_cache: bool = False

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    ticker: Optional[str] = None


#This file define design/blueprint