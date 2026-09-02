"""Schemas para el proceso de generacion."""
from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    mode: str = "auto"                    # auto, prompt, manuscript, expand, continue
    genres: list[str]                     # minimo 1
    style: str = "anime"                  # id del estilo visual
    duration_minutes: int = Field(default=22, ge=1)
    num_characters: int = Field(default=3, ge=2, le=6)
    tone: int = Field(default=70, ge=0, le=100)
    platforms: list[str] = Field(default_factory=lambda: ["youtube"])
    prompt_text: str | None = None
    continue_from_project_id: int | None = None
    # Soporte de capítulos
    chapters_mode: bool = False           # True para dividir en capítulos
    chapter_duration_minutes: int = Field(default=20, ge=5, le=60)


class AgentLogEntry(BaseModel):
    agent: str
    message: str
    log_type: str = "info"  # info, success, warning, error
    timestamp: float = 0.0


class ChapterInfo(BaseModel):
    chapter_number: int
    title: str
    synopsis: str | None = None
    duration_minutes: int
    start_scene: int
    end_scene: int
    video_path: str | None = None


class GenerationStatus(BaseModel):
    project_id: int | None = None
    phase: str = "idle"  # idle, generating, shorts, done
    current_agent_index: int = -1
    progress: int = 0
    scenes_generated: int = 0
    total_scenes: int = 0
    current_chapter: int = 0
    total_chapters: int = 1
    log: list[AgentLogEntry] = Field(default_factory=list)
    chapters: list[ChapterInfo] = Field(default_factory=list)
    error: str | None = None
