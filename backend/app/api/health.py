from fastapi import APIRouter
from app.core.config import settings
router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "env": settings.app_env,
    }

# health.py = quick system status check (app + env + external API)