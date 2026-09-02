"""Agente Storyboard: descompone la historia en escenas visuales."""
from __future__ import annotations

import logging

from backend.app.services.llm_service import generate

logger = logging.getLogger(__name__)


async def run_storyboard(state: dict) -> dict:
    """Enriquece cada escena con datos de storyboard."""
    logger.info("[Storyboard] Descomponiendo en escenas visuales...")

    style = state.get("style", "anime")
    scenes = state.get("scenes", [])
    characters = state.get("characters", [])

    char_map = {c["name"]: c for c in characters}

    for scene in scenes:
        chars_in_scene = scene.get("character_names", [])
        char_descs = [char_map.get(n, {}).get("appearance", n) for n in chars_in_scene]

        prompt = f"""Genera un prompt de imagen para esta escena de una historia narrada.
Estilo: {style}
Emocion: {scene['emotion']}
Camara: {scene['camera']}
Personajes en escena: {', '.join(char_descs)}
Accion: {scene['narration'][:150]}

Responde SOLO con el prompt de imagen, sin comillas ni explicaciones."""

        try:
            image_prompt = generate(prompt, system_prompt="Generas prompts detallados para IA de imagenes. Solo el prompt, nada mas.", max_tokens=256)
            scene["image_prompt"] = image_prompt.strip()
        except Exception:
            scene["image_prompt"] = f"{style} style, {scene['emotion']} mood, {scene['camera']} shot, dramatic lighting"

    logger.info("[Storyboard] %d escenas procesadas", len(scenes))
    return state