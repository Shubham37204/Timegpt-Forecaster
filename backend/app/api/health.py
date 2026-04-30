from fastapi import APIRouter, Request
from app.core.config import settings
router = APIRouter()


@router.get("/health")
async def health_check(request: Request):
    return {
        "status": "ok",
        "env": settings.app_env,
        "nixtla_api": request.app.state.nixtla_api_ok,
    }

# health.py = quick system status check (app + env + external API)