from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import forecast, health
from app.core.config import settings
from app.core.logging import setup_logging, get_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = get_logger(__name__)
    logger.info("app_starting", env=settings.app_env)
    yield
    logger.info("app_stopping")

app = FastAPI(title="TimeGPT Forecaster", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# in main.py
@app.get("/")
async def root():
    return {"message": "TimeGPT Forecaster API", "docs": "/docs"}

app.include_router(forecast.router, prefix="/api/v1")
app.include_router(health.router, prefix="")