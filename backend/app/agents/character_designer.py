"""Agente Diseñador de Personajes: crea Character Bible y consistencia visual."""
from __future__ import annotations

import hashlib
import logging

from backend.app.services.llm_service import generate

logger = logging.getLogger(__name__)


async def run_character_designer(state: dict) -> dict:
    """Enriquece los personajes con datos de consistencia visual."""
    logger.info("[Diseñador Chars] Creando Character Bible...")

    style = state.get("style", "anime")
    for char in state.get("characters", []):
        # Asegurar que la apariencia incluye el estilo
        appearance = char.get("appearance", "")
        if style.lower() not in appearance.lower():
            char["appearance_full"] = f"{style} style, {appearance}"
        else:
            char["appearance_full"] = appearance

        # El modelo visual responde de forma más fiable a descripciones en
        # inglés. Se traduce una única vez y se conserva sin alterarla en toda
        # la producción; nunca se sustituye por una foto de otro proyecto.
        visual_description = generate(
            "Translate the following character appearance into concise, precise English "
            "tags for an anime image model. Preserve gender, age range, hair, eyes, "
            "clothes, scars and accessories. Return only the English visual description.\n\n"
            f"{appearance}",
            system_prompt="You are an expert anime character designer. Return only English image tags.",
            max_tokens=180,
        ).strip().strip('"')
        char["visual_description"] = visual_description

        # Esta descripción es la "identidad canónica". Nunca se sustituye por
        # nombres genéricos o por una imagen anterior de la base de datos.
        # Se inyecta tanto en el retrato como en cada escena donde participa.
        identity_prompt = (
            f"{style} style, {visual_description}, "
            "same character identity, same face, same hairstyle, same eye color, "
            "same outfit and accessories"
        )
        char["identity_prompt"] = identity_prompt

        # Una semilla fija por personaje hace que el modelo conserve rasgos
        # visuales incluso en escenas con acciones y encuadres distintos.
        char["reference_seed"] = int(
            hashlib.sha256(identity_prompt.encode("utf-8")).hexdigest()[:12], 16
        ) % 2_147_483_647

        # Generar prompt de referencia para la ficha visible del proyecto.
        char["ref_prompt"] = (
            f"full body character reference sheet, {identity_prompt}, "
            "front, three-quarter and side views, neutral pose, clean light background, "
            "professional anime character design, no text"
        )

    logger.info("[Diseñador Chars] %d personajes procesados", len(state.get("characters", [])))
    return state
