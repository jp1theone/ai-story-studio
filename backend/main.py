"""Punto de entrada de la API."""
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base, run_migrations
from backend.app.api.router import api_router
from backend.app.api.ws import router as ws_router

import asyncio
from backend.app.api import ws


def configure_logging() -> None:
    """Guarda los fallos de producción en un archivo persistente."""
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    root_logger = logging.getLogger()
    log_file = log_dir / "backend.log"
    if not any(
        isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == log_file
        for handler in root_logger.handlers
    ):
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Crear/actualizar tablas al arrancar
    Base.metadata.create_all(bind=engine)
    # 2. Migración de columnas nuevas (sin borrar datos)
    run_migrations()
    # 3. Guardar el event loop para WebSocket broadcasts desde threads
    ws.main_loop = asyncio.get_running_loop()
    yield


app = FastAPI(
    title="AI Story Studio",
    description="API del Estudio Autónomo de Producción de Contenido — Videos de Anime Narrados",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
# WebSocket sin prefijo /api: coincide con el proxy y cliente del frontend.
app.include_router(ws_router, tags=["websocket"])


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    """Confirma que el backend está activo sin devolver un 404 confuso."""
    return {
        "status": "ok",
        "service": "AI Story Studio API",
        "docs": "/docs",
        "api": "/api/health",
    }


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    """Endpoint ligero para el lanzador y diagnósticos de la aplicación."""
    return {"status": "ok"}
