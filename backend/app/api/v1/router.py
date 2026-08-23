"""
Aggregates all /api/v1 domain routers. Memory registered in Phase W4.5;
Tasks registered in Phase W6.
"""
from fastapi import APIRouter

from app.api.v1.memory import router as memory_router
from app.api.v1.tasks import router as tasks_router

api_router = APIRouter()
api_router.include_router(memory_router)
api_router.include_router(tasks_router)
