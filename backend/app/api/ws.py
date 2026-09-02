"""WebSocket para streaming de logs de generacion en tiempo real."""
import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Gestiona conexiones WebSocket por proyecto."""

    def __init__(self) -> None:
        self.active: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: int) -> None:
        await websocket.accept()
        self.active.setdefault(project_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, project_id: int) -> None:
        connections = self.active.get(project_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self.active.pop(project_id, None)

    async def broadcast(self, project_id: int, data: dict) -> None:
        disconnected: list[WebSocket] = []
        for ws in list(self.active.get(project_id, [])):
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws, project_id)


manager = ConnectionManager()


@router.websocket("/ws/generation/{project_id}")
async def ws_generation(websocket: WebSocket, project_id: int):
    await manager.connect(websocket, project_id)
    try:
        while True:
            # Mantener conexion abierta; los mensajes vienen del backend
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)


main_loop = None


def broadcast_log(project_id: int, agent: str, message: str, log_type: str = "info") -> None:
    """Funcion helper para enviar logs desde las tareas."""
    import asyncio
    global main_loop
    if main_loop is not None:
        try:
            asyncio.run_coroutine_threadsafe(
                manager.broadcast(project_id, {
                    "type": "log",
                    "agent": agent,
                    "message": message,
                    "log_type": log_type,
                }),
                main_loop
            )
        except Exception as e:
            logger.error("Error broadcasting log: %s", e)
    else:
        logger.info("[%s] %s: %s", log_type, agent, message)


def broadcast_progress(project_id: int, agent_index: int, progress: int, **extra) -> None:
    """Funcion helper para enviar actualizaciones de progreso."""
    import asyncio
    global main_loop
    if main_loop is not None:
        try:
            asyncio.run_coroutine_threadsafe(
                manager.broadcast(project_id, {
                    "type": "progress",
                    "agent_index": agent_index,
                    "progress": progress,
                    **extra,
                }),
                main_loop
            )
        except Exception as e:
            logger.error("Error broadcasting progress: %s", e)
    else:
        logger.info("Progress: %d%% (Agent %d)", progress, agent_index)
