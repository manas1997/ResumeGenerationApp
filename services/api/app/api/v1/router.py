from fastapi import APIRouter

from app.api.v1.endpoints import health, tailoring

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(tailoring.router, prefix="/tailoring-runs", tags=["tailoring"])

