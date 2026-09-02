"""Agente Generador de Voces: sintetiza audio para cada escena.
Con soporte de capítulos, progreso en tiempo real y fallback robusto.
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from backend.app.services.tts_service import tts_service
from backend.config import settings

logger = logging.getLogger(__name__)


async def run_voice_generator(state: dict) -> dict:
    """Genera la narración de cada escena con soporte multi-capítulo."""
    logger.info("[Gen. Voces] Iniciando síntesis de voz...")
    tts_service.load_model()

    project_id = state.get("project_id", "temp")
    output_dir = settings.output_dir / str(project_id) / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)

    scenes = state.get("scenes", [])
    characters = state.get("characters", [])
    char_voice_map = {c["name"]: c.get("voice_type", "neutral") for c in characters}

    total = len(scenes)
    generated = 0
    failed = 0

    for i, scene in enumerate(scenes):
        chapter_num = scene.get("chapter_number", 1)
        scene_num = scene["scene_number"]
        logger.info(
            "[Gen. Voces] Cap.%d — Escena %d/%d: %s",
            chapter_num, i + 1, total, scene.get("title", "")
        )

        try:
            # Subcarpeta por capítulo para organización
            ch_dir = output_dir / f"chapter_{chapter_num:02d}"
            ch_dir.mkdir(parents=True, exist_ok=True)
            audio_path = ch_dir / f"scene_{scene_num:04d}.wav"

            narration = scene.get("narration", "Escena sin narración.")
            voice_type = char_voice_map.get(
                (scene.get("character_names") or [""])[0], "neutral"
            )

            # Ejecutar en executor para no bloquear el event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda p=audio_path, n=narration, v=voice_type: tts_service.generate_speech(
                    text=n, output_path=p, voice_type=v
                )
            )

            if audio_path.exists() and audio_path.stat().st_size > 100:
                scene["audio_path"] = str(audio_path)
                generated += 1
                logger.info(
                    "[Gen. Voces] ✅ Escena %d — %.1f KB",
                    scene_num, audio_path.stat().st_size / 1024
                )
            else:
                raise RuntimeError("Archivo de audio vacío")

        except Exception as e:
            logger.error("[Gen. Voces] ❌ Escena %d: %s", scene_num, e)
            scene["audio_path"] = None
            failed += 1

    tts_service.unload_model()
    state["voices_generated"] = generated
    logger.info(
        "[Gen. Voces] Completado: %d/%d pistas OK, %d fallidas",
        generated, total, failed
    )
    return state