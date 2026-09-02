"""Endpoints de CRUD y descarga de proyectos."""
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.app.models.project import Project, ProjectStatus
from backend.app.schemas.project import ProjectRead, ProjectList

router = APIRouter()


def _project_output_dir(project_id: int) -> Path:
    """Devuelve el directorio de salida de un proyecto sin aceptar escapes de ruta."""
    output_root = settings.output_dir.resolve()
    project_dir = (output_root / str(project_id)).resolve()
    if output_root not in project_dir.parents:
        raise HTTPException(status_code=400, detail="Ruta de proyecto inválida")
    return project_dir


@router.get("/{project_id}/download")
def download_project_file(
    project_id: int,
    path: str | None = None,
    platform: str | None = None,
    db: Session = Depends(get_db),
):
    """Descarga un archivo generado, limitado siempre a la salida del proyecto."""
    if not db.query(Project.id).filter(Project.id == project_id).first():
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    project_dir = _project_output_dir(project_id)
    if path:
        requested = Path(path)
        candidate = requested.resolve() if requested.is_absolute() else (project_dir / requested).resolve()
    elif platform:
        if platform not in {"youtube", "tiktok", "facebook", "shorts"}:
            raise HTTPException(status_code=400, detail="Plataforma no válida")
        platform_dir = project_dir / platform
        candidates = sorted(platform_dir.glob("*.mp4"), key=lambda item: item.stat().st_mtime, reverse=True)
        candidate = candidates[0].resolve() if candidates else project_dir / "__missing__"
    else:
        raise HTTPException(status_code=400, detail="Indica un archivo o plataforma para descargar")

    if project_dir not in candidate.parents or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Archivo generado no encontrado")
    return FileResponse(candidate, filename=candidate.name, media_type="video/mp4")


@router.get("/{project_id}/scene/{scene_id}/image")
def get_scene_image(project_id: int, scene_id: int, db: Session = Depends(get_db)):
    """Entrega la imagen de una escena para las vistas del proyecto."""
    from backend.app.models.project import Scene

    scene = db.query(Scene).filter(Scene.id == scene_id, Scene.project_id == project_id).first()
    if not scene or not scene.image_path:
        raise HTTPException(status_code=404, detail="Imagen de escena no encontrada")
    image_path = Path(scene.image_path).resolve()
    project_dir = _project_output_dir(project_id)
    if project_dir not in image_path.parents or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo de imagen no encontrado")
    return FileResponse(image_path, media_type="image/jpeg")


@router.get("/{project_id}/character/{character_id}/image")
def get_character_image(project_id: int, character_id: int, db: Session = Depends(get_db)):
    """Entrega la ficha visual persistente de un personaje."""
    from backend.app.models.project import Character

    character = db.query(Character).filter(
        Character.id == character_id, Character.project_id == project_id
    ).first()
    if not character or not character.reference_image_path:
        raise HTTPException(status_code=404, detail="Ficha visual no encontrada")
    image_path = Path(character.reference_image_path).resolve()
    project_dir = _project_output_dir(project_id)
    if project_dir not in image_path.parents or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo de ficha no encontrado")
    return FileResponse(image_path, media_type="image/jpeg")


@router.get("", response_model=list[ProjectList])
def list_projects(db: Session = Depends(get_db)):
    """Lista todos los proyectos con conteo de escenas."""
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    result = []
    for p in projects:
        item = ProjectList.model_validate(p)
        item.scene_count = len(p.scenes)
        result.append(item)
    return result


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Obtiene un proyecto completo con escenas, personajes y cortos."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Elimina un proyecto y todos sus datos asociados."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    db.delete(project)
    db.commit()
    return {"ok": True}
