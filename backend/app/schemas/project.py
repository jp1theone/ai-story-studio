"""Schemas Pydantic para proyectos."""
from datetime import datetime
from pydantic import BaseModel


class CharacterRead(BaseModel):
    id: int
    name: str
    role: str
    description: str
    appearance: str
    voice_type: str
    reference_image_path: str | None = None

    model_config = {"from_attributes": True}


class SceneRead(BaseModel):
    id: int
    scene_number: int
    chapter_number: int | None = 1
    title: str
    narration: str
    emotion: str
    camera: str
    image_prompt: str
    duration_seconds: int
    character_names: list[str]
    image_path: str | None = None
    audio_path: str | None = None

    model_config = {"from_attributes": True}


class ChapterRead(BaseModel):
    id: int
    chapter_number: int
    title: str
    synopsis: str | None = None
    duration_minutes: int
    cliffhanger: str | None = None
    video_path: str | None = None
    start_scene_number: int
    end_scene_number: int

    model_config = {"from_attributes": True}


class ShortRead(BaseModel):
    id: int
    title: str
    hook: str
    start_scene_number: int
    end_scene_number: int
    duration_string: str
    platforms: list[str]
    video_path: str | None = None

    model_config = {"from_attributes": True}


class ProjectRead(BaseModel):
    id: int
    title: str
    synopsis: str | None
    genres: list[str]
    style: str
    duration_minutes: int
    tone: int
    mode: str
    platforms: list[str]
    status: str
    seo_data: dict | None
    chapters_mode: bool = False
    chapter_duration_minutes: int = 20
    total_chapters: int = 1
    created_at: datetime
    scenes: list[SceneRead] = []
    characters: list[CharacterRead] = []
    shorts: list[ShortRead] = []
    chapters: list[ChapterRead] = []

    model_config = {"from_attributes": True}


class ProjectList(BaseModel):
    id: int
    title: str
    genres: list[str]
    style: str
    duration_minutes: int
    total_chapters: int = 1
    chapters_mode: bool = False
    status: str
    created_at: datetime
    scene_count: int = 0

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    """No se usa directamente para crear; la generacion crea el proyecto."""
    pass
