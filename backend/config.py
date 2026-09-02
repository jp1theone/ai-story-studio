"""Configuracion centralizada. Lee de .env con valores por defecto."""
import json
from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
APP_SETTINGS_FILE = BASE_DIR / ".app_settings.json"


def default_content_dir() -> Path:
    """Biblioteca final de entregas, independiente de los archivos temporales."""
    return Path.home() / "Desktop" / "Contenido"


def load_content_dir() -> Path:
    try:
        value = json.loads(APP_SETTINGS_FILE.read_text(encoding="utf-8")).get("content_dir")
        if value:
            return Path(value).expanduser()
    except (OSError, ValueError, json.JSONDecodeError):
        pass
    return default_content_dir()


class Settings(BaseSettings):
    # LLM
    llm_model_path: Path = BASE_DIR / "models" / "llm" / "qwen2.5-7b-instruct-q4_k_m.gguf"
    llm_n_gpu_layers: int = 28
    llm_context_size: int = 8192
    llm_temperature: float = 0.8

    # ComfyUI
    comfyui_url: str = "http://127.0.0.1:8188"
    comfyui_workflow_dir: Path = BASE_DIR / "comfyui" / "workflows"
    # Formato cinematográfico base para el video horizontal. Los shorts se
    # reencuadran al exportar, sin sacrificar la composición de la escena.
    image_width: int = 768
    image_height: int = 432
    image_steps: int = 30
    image_cfg: float = 7.5

    # TTS
    tts_model_path: Path = BASE_DIR / "models" / "tts" / "F5-TTS"
    tts_language: str = "es"

    # FFmpeg
    ffmpeg_path: str = "ffmpeg"
    output_dir: Path = BASE_DIR / "output"
    content_dir: Path = load_content_dir()

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # DB
    database_url: str = "sqlite:///./ai_story_studio.db"

    model_config = {"env_file": BASE_DIR / ".env", "env_file_encoding": "utf-8"}


settings = Settings()


def set_content_dir(path: Path) -> Path:
    """Actualiza y persiste la carpeta de entregas elegida por el usuario."""
    resolved = path.expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    (resolved / "Videos").mkdir(exist_ok=True)
    (resolved / "Shorts").mkdir(exist_ok=True)
    APP_SETTINGS_FILE.write_text(
        json.dumps({"content_dir": str(resolved)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    settings.content_dir = resolved
    return resolved
