"""Router principal que agrupa todas las rutas de la API."""
from fastapi import APIRouter

from backend.app.api.projects import router as projects_router
from backend.app.api.generation import router as generation_router
from backend.app.api.settings import router as settings_router

api_router = APIRouter()
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(generation_router, prefix="/generation", tags=["generation"])
api_router.include_router(settings_router, prefix="/settings", tags=["settings"])
