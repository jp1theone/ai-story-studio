"""Agente QA: control de calidad final."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def run_qa(state: dict) -> dict:
    """Ejecuta checks de calidad finales."""
    logger.info("[QA] Ejecutando control de calidad...")

    checks = []
    total_duration = sum(s.get("duration_seconds", 0) for s in state.get("scenes", []))
    req_duration = state.get("duration_minutes", 1)
    min_duration = req_duration * 60

    # Check duracion minima
    if total_duration >= min_duration:
        checks.append({"check": f"Duracion minima ({req_duration} min)", "passed": True, "detail": f"{total_duration}s >= {min_duration}s"})
    else:
        checks.append({"check": f"Duracion minima ({req_duration} min)", "passed": False, "detail": f"{total_duration}s < {min_duration}s"})

    # Check imagenes
    img_count = sum(1 for s in state.get("scenes", []) if s.get("image_path"))
    total = len(state.get("scenes", []))
    checks.append({"check": "Imagenes generadas", "passed": img_count == total, "detail": f"{img_count}/{total}"})

    # Check audio
    aud_count = sum(1 for s in state.get("scenes", []) if s.get("audio_path"))
    checks.append({"check": "Pistas de audio", "passed": aud_count == total, "detail": f"{aud_count}/{total}"})

    # Check personajes
    chars = state.get("characters", [])
    checks.append({"check": "Personajes definidos", "passed": len(chars) >= 2, "detail": f"{len(chars)} personajes"})

    # Check SEO
    checks.append({"check": "Metadatos SEO", "passed": bool(state.get("seo_data")), "detail": "SEO" + (" generado" if state.get("seo_data") else " faltante")})

    all_passed = all(c["passed"] for c in checks)
    state["qa_checks"] = checks
    state["qa_passed"] = all_passed

    if all_passed:
        logger.info("[QA] Todos los checks pasaron.")
    else:
        failed = [c for c in checks if not c["passed"]]
        logger.warning("[QA] Checks fallidos: %s", [c["check"] for c in failed])

    return state