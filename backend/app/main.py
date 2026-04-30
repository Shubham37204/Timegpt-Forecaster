from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import forecast, health
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.services.timegpt_service import validate_api_key

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = get_logger(__name__)
    
    # validate once at startup, store on app.state
    app.state.nixtla_api_ok = validate_api_key()
    
    logger.info("app_starting", env=settings.app_env, nixtla_ok=app.state.nixtla_api_ok)
    yield
    logger.info("app_stopping")


app = FastAPI(
    title="TimeGPT Forecaster",
    lifespan=lifespan
)

# 🔹 CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forecast.router, prefix="/api/v1")
app.include_router(health.router, prefix="")
