"""Agente Editor: verifica coherencia, ritmo y calidad."""
from __future__ import annotations

import logging

from backend.app.services.llm_service import generate

logger = logging.getLogger(__name__)


async def run_editor(state: dict) -> dict:
    """Revisa y mejora la historia generada."""
    logger.info("[Editor] Verificando coherencia narrativa...")

    scenes_text = "\n".join(
        f"Escena {s['scene_number']}: {s['title']} ({s.get('duration_seconds',0)}s) - {s['narration'][:100]}..."
        for s in state.get("scenes", [])
    )
    chars_text = "\n".join(
        f"- {c['name']} ({c['role']}): {c['description'][:80]}"
        for c in state.get("characters", [])
    )

    prompt = f"""Revisa esta historia y califica su calidad del 0 al 100.
Si hay problemas, sugiere correcciones breves.

PERSONAJES:
{chars_text}

ESCENAS:
{scenes_text}

Responde SOLO en JSON:
{{"score": 85, "issues": ["problema1"], "fixes_applied": ["correccion1"]}}"""

    try:
        raw = generate(prompt, system_prompt="Eres un editor literario estricto. Responde solo JSON.", max_tokens=1024)
        if "```" in raw:
            raw = raw.split("```")[1].split("```")[0]
        import json
        result = json.loads(raw.strip())
        state["editor_score"] = result.get("score", 70)
        logger.info("[Editor] Quality score: %d/100", state["editor_score"])
    except Exception as e:
        logger.warning("[Editor] No se pudo parsear la evaluacion: %s", e)
        state["editor_score"] = 70

    return state