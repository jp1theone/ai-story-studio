"""Agente SEO: genera titulos, descripciones y hashtags por plataforma."""
from __future__ import annotations

import logging

from backend.app.services.llm_service import generate

logger = logging.getLogger(__name__)


async def run_seo_generator(state: dict) -> dict:
    """Genera metadatos SEO para cada plataforma seleccionada."""
    logger.info("[SEO] Generando metadatos multiplataforma...")

    title = state.get("title", "")
    synopsis = state.get("synopsis", "")
    genres = state.get("genres", [])
    platforms = state.get("platforms", ["youtube"])

    prompt = f"""Genera metadatos SEO para un video narrado.

Titulo: {title}
Sinopsis: {synopsis}
Generos: {', '.join(genres)}
Plataformas: {', '.join(platforms)}

Responde SOLO en JSON:
{{
  "youtube": {{
    "title": "Titulo SEO para YouTube (max 100 chars)",
    "description": "Descripcion completa con timestamps, min 300 chars",
    "tags": ["hashtag1", "hashtag2", ...]
  }},
  "tiktok": {{
    "title": "Titulo corto y viral (max 60 chars)",
    "description": "Descripcion breve",
    "tags": ["#hashtag1", "#hashtag2", ...]
  }},
  "facebook": {{
    "title": "Titulo para Facebook",
    "description": "Descripcion para Facebook",
    "tags": ["hashtag1", "hashtag2", ...]
  }},
  "shorts": {{
    "title": "Titulo para YouTube Shorts",
    "description": "Descripcion breve",
    "tags": ["#hashtag1", "#hashtag2", ...]
  }},
  "thumbnail_text": "Texto superpuesto a la miniatura (max 50 chars)"
}}"""

    try:
        raw = generate(prompt, system_prompt="Eres un experto en SEO para YouTube y redes sociales. Solo JSON.", max_tokens=2048)
        if "```" in raw:
            raw = raw.split("```")[1].split("```")[0]
        import json
        state["seo_data"] = json.loads(raw.strip())
    except Exception as e:
        logger.warning("[SEO] Error generando SEO: %s. Usando fallback.", e)
        state["seo_data"] = {
            "youtube": {
                "title": title,
                "description": synopsis,
                "tags": ["#storytime", "#narrado"] + [f"#{g}" for g in genres],
            }
        }

    # Seleccionar miniatura: escena con mayor tension emocional
    emotions_rank = {"tragedia": 10, "impacto": 9, "giro": 8, "accion": 7, "drama": 6}
    scenes = state.get("scenes", [])
    best = max(scenes, key=lambda s: emotions_rank.get(s.get("emotion", ""), 0))
    state["thumbnail_scene_id"] = best.get("scene_number")
    state["thumbnail_text"] = state.get("seo_data", {}).get("thumbnail_text", "")

    logger.info("[SEO] Metadatos generados para %d plataformas", len(platforms))
    return state