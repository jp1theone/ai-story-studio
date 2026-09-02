"""Endpoints de generacion de historias."""
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.app.models.project import Project, ProjectStatus, Scene, Character
from backend.app.schemas.generation import GenerationRequest, GenerationStatus
from backend.app.tasks.generation_task import run_full_generation

router = APIRouter()


@router.post("/start", response_model=GenerationStatus)
def start_generation(
    req: GenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Inicia la generacion de una nueva historia."""
    if len(req.genres) < 1:
        raise HTTPException(status_code=400, detail="Selecciona al menos un género")
    # Crear proyecto en DB
    project = Project(
        title="Generando...",
        genres=req.genres,
        style=req.style,
        duration_minutes=req.duration_minutes,
        tone=req.tone,
        mode=req.mode,
        prompt_text=req.prompt_text,
        platforms=req.platforms,
        chapters_mode=req.chapters_mode,
        chapter_duration_minutes=req.chapter_duration_minutes,
        status=ProjectStatus.GENERATING,
    )
    try:
        db.add(project)
        db.commit()
        db.refresh(project)
    except Exception as exc:
        db.rollback()
        # Devolver el fallo de creación al creador en vez de un 500 opaco.
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo crear el proyecto en la base de datos: {exc}",
        ) from exc

    # Lanzar tarea en background
    background_tasks.add_task(
        run_full_generation,
        project_id=project.id,
        genres=req.genres,
        style=req.style,
        duration_minutes=req.duration_minutes,
        num_characters=req.num_characters,
        tone=req.tone,
        mode=req.mode,
        prompt_text=req.prompt_text,
        platforms=req.platforms,
        continue_from_project_id=req.continue_from_project_id,
        chapters_mode=req.chapters_mode,
        chapter_duration_minutes=req.chapter_duration_minutes,
    )

    return GenerationStatus(
        project_id=project.id,
        phase="generating",
        current_agent_index=0,
        progress=0,
    )


@router.get("/status/{project_id}", response_model=GenerationStatus)
def get_generation_status(project_id: int, db: Session = Depends(get_db)):
    """Consulta el estado actual de una generación."""
    from backend.app.tasks.generation_task import get_status
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if project.status == ProjectStatus.COMPLETED:
        return GenerationStatus(
            project_id=project.id,
            phase="done",
            progress=100,
            total_chapters=project.total_chapters or 1,
        )
    status = get_status(project_id)
    if status is None:
        return GenerationStatus(
            project_id=project.id,
            phase=("done" if project.status == ProjectStatus.COMPLETED
                   else "failed" if project.status == ProjectStatus.FAILED
                   else "generating" if project.status == ProjectStatus.GENERATING
                   else "idle"),
            progress=100 if project.status == ProjectStatus.COMPLETED else 0,
            total_chapters=project.total_chapters or 1,
        )
    return GenerationStatus(**status)


@router.post("/shorts/{project_id}")
def generate_shorts(project_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Genera cortos a partir de un proyecto completado."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if project.status != ProjectStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="El proyecto debe estar completado")

    from backend.app.tasks.generation_task import run_shorts_generation
    background_tasks.add_task(run_shorts_generation, project_id=project.id)
    return {"ok": True, "message": "Generación de cortos iniciada"}
