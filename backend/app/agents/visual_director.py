"""Agente Director Visual: configura estilo, paleta y modelo."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

STYLE_MODEL_MAP = {
    "anime": "Pony Diffusion V6 XL",
    "anime-cine": "AnimagineXL v3.1",
    "realista": "Juggernaut XL v9",
    "semi-realista": "Juggernaut XL v9",
    "manhwa": "Pony Diffusion V6 XL",
    "manga": "Pony Diffusion V6 XL",
}

STYLE_NEGATIVE = {
    "anime": "lowres, bad anatomy, bad hands, text, error, missing fingers, cropped, worst quality, low quality, jpeg artifacts, blurry",
    "anime-cine": "lowres, bad anatomy, bad hands, text, error, deformed, ugly, blurry",
    "realista": "lowres, bad anatomy, bad hands, illustration, anime, cartoon, painting, drawing",
    "semi-realista": "lowres, bad anatomy, photorealistic, hyperrealistic, bad hands",
    "manhwa": "lowres, bad anatomy, bad hands, text, error, japanese style, traditional manga",
    "manga": "lowres, bad anatomy, bad hands, text, color, error",
}


async def run_visual_director(state: dict) -> dict:
    """Configura los parametros visuales para todas las escenas."""
    logger.info("[Director Visual] Configurando estilo visual...")

    style = state.get("style", "anime")
    state["visual_model"] = STYLE_MODEL_MAP.get(style, "SDXL")
    state["visual_negative"] = STYLE_NEGATIVE.get(style, STYLE_NEGATIVE["anime"])

    for scene in state.get("scenes", []):
        if "negative_prompt" not in scene:
            scene["negative_prompt"] = state["visual_negative"]

    logger.info("[Director Visual] Modelo: %s", state["visual_model"])
    return state