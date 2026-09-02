"""Agente Generador de Imágenes reales mediante ComfyUI."""
from __future__ import annotations

import asyncio
import logging

from backend.app.services.llm_service import unload_llm
from backend.app.services.comfyui_service import comfyui_service
from backend.config import settings

logger = logging.getLogger(__name__)


async def run_image_generator(state: dict) -> dict:
    """Genera las imágenes de todas las escenas mediante ComfyUI."""
    logger.info("[Gen. Imágenes] Descargando LLM de VRAM...")
    unload_llm()

    project_id = state.get("project_id", "temp")
    scenes = state.get("scenes", [])
    style = state.get("style", "anime")

    total = len(scenes)
    generated = 0
    failed = 0

    # 1) Fijar una ficha visual por personaje ANTES de producir las escenas.
    # Estas fichas se guardan con el proyecto y son la base de la continuidad.
    characters = state.get("characters", [])
    character_lookup = {char.get("name"): char for char in characters}
    character_dir = settings.output_dir / str(project_id) / "characters"
    character_dir.mkdir(parents=True, exist_ok=True)
    reference_failures: list[str] = []
    for character in characters:
        reference_prompt = character.get("ref_prompt") or (
            f"{style} character reference portrait, {character.get('appearance', '')}, "
            "front view, clean background, consistent facial features, no text"
        )
        try:
            reference_path = await comfyui_service.generate_image(
                prompt_text=reference_prompt,
                style=style,
                seed=character.get("reference_seed"),
                output_dir=character_dir,
            )
            character["reference_image_path"] = str(reference_path)
            logger.info("[Gen. Imágenes] Ficha creada: %s", character.get("name"))
        except Exception as exc:
            name = character.get("name", "personaje")
            reference_failures.append(name)
            logger.error("[Gen. Imágenes] No se pudo crear ficha de %s: %s", name, exc)

    if reference_failures:
        raise RuntimeError(
            "No se pudieron crear las fichas visuales de: "
            f"{', '.join(reference_failures)}. No se generarán escenas sin referencias."
        )

    for i, scene in enumerate(scenes):
        chapter_num = scene.get("chapter_number", 1)
        scene_num = scene["scene_number"]

        # Directorio organizado por capítulo
        output_dir = settings.output_dir / str(project_id) / "scenes" / f"chapter_{chapter_num:02d}"
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "[Gen. Imágenes] Cap.%d — Escena %d/%d: %s",
            chapter_num, i + 1, total, scene.get("title", "")
        )

        try:
            present_characters = [character_lookup[name] for name in scene.get("character_names", []) if name in character_lookup]
            identity_lock = ", ".join(
                char.get("identity_prompt", char.get("appearance_full", char.get("appearance", "")))
                for char in present_characters
            )
            reference_paths = [
                char["reference_image_path"]
                for char in present_characters
                if char.get("reference_image_path")
            ]
            # Para una pareja o un elenco, la semilla de la escena se deriva de
            # sus identidades, no del número de escena. Así no cambia la cara
            # del MC/FMC al pasar de una playa a una ciudad.
            identity_seed = sum(int(char.get("reference_seed", 0)) for char in present_characters) or None
            scene_prompt = (
                f"{scene.get('image_prompt', '')}. "
                f"SCENE ACTION: {scene.get('narration', '')[:500]}. "
                f"CHARACTER CONTINUITY — reproduce exactly these established characters: {identity_lock}. "
                "Show every named character performing the scene action; no random people, no text, no collage."
            )
            img_path = await comfyui_service.generate_image(
                prompt_text=scene_prompt,
                style=style,
                seed=identity_seed,
                character_refs=reference_paths,
                output_dir=output_dir,
            )
            scene["image_path"] = str(img_path)
            generated += 1
            logger.info("[Gen. Imágenes] ✅ Escena %d — %s", scene_num, img_path.name)

        except Exception as e:
            logger.error("[Gen. Imágenes] ❌ Escena %d: %s", scene_num, e)
            scene["image_path"] = None
            failed += 1

        # Pequeña pausa entre escenas para no saturar ComfyUI
        if i < total - 1:
            await asyncio.sleep(0.1)

    state["images_generated"] = generated
    logger.info(
        "[Gen. Imágenes] Completado: %d/%d imágenes OK, %d fallidas",
        generated, total, failed
    )
    if failed:
        raise RuntimeError(
            f"La generación visual falló en {failed} de {total} escenas. "
            "No se ensamblará un video con imágenes faltantes o de respaldo."
        )
    return state
