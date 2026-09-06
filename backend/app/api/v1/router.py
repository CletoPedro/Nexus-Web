"""
Aggregates all /api/v1 domain routers. Memory registered in Phase W4.5;
Tasks in Phase W6; Documents, Inventory, Timeline in Phase W7/W8/W9.
"""
from fastapi import APIRouter

from app.api.v1.documents import router as documents_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.memory import router as memory_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.timeline import router as timeline_router

api_router = APIRouter()
api_router.include_router(memory_router)
api_router.include_router(tasks_router)
api_router.include_router(documents_router)
api_router.include_router(inventory_router)
api_router.include_router(timeline_router)
