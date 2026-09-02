"""Configuración editable de la biblioteca de entregas."""
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.config import settings, set_content_dir

router = APIRouter()


class OutputFolderUpdate(BaseModel):
    path: str


@router.get("/output-folder")
def get_output_folder() -> dict[str, str]:
    return {"path": str(settings.content_dir)}


@router.put("/output-folder")
def update_output_folder(body: OutputFolderUpdate) -> dict[str, str]:
    path = body.path.strip()
    if not path:
        raise HTTPException(status_code=400, detail="Indica una carpeta válida")
    try:
        return {"path": str(set_content_dir(Path(path)))}
    except OSError as exc:
        raise HTTPException(status_code=400, detail=f"No se pudo preparar la carpeta: {exc}") from exc
