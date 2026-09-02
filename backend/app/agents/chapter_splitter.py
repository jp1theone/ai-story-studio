"""Agente divisor de capítulos: organiza las escenas en capítulos y genera metadata."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def run_chapter_splitter(state: dict) -> dict:
    """Organiza las escenas en capítulos y enriquece la metadata de cada uno."""
    logger.info("[ChapterSplitter] Organizando capítulos...")

    use_chapters = state.get("use_chapters", False)
    num_chapters = state.get("num_chapters", 1)
    scenes = state.get("scenes", [])
    chapters_meta_raw = state.get("chapters_meta", [])

    if not use_chapters or num_chapters <= 1:
        # Sin capítulos: todo es capítulo 1
        state["chapters"] = [{
            "chapter_number": 1,
            "title": state.get("title", "Historia Completa"),
            "synopsis": state.get("synopsis", ""),
            "duration_minutes": state.get("duration_minutes", 22),
            "cliffhanger": None,
            "start_scene_number": 1,
            "end_scene_number": len(scenes),
        }]
        logger.info("[ChapterSplitter] Modo capítulo único.")
        return state

    # Agrupar escenas por capítulo
    chapters_built: list[dict] = []
    scenes_by_chapter: dict[int, list] = {}
    for scene in scenes:
        ch = scene.get("chapter_number", 1)
        scenes_by_chapter.setdefault(ch, []).append(scene)

    # Crear metadata para cada capítulo
    meta_lookup = {m.get("chapter_number"): m for m in chapters_meta_raw}

    for ch_num in range(1, num_chapters + 1):
        ch_scenes = scenes_by_chapter.get(ch_num, [])
        if not ch_scenes:
            continue

        duration_secs = sum(s.get("duration_seconds", 0) for s in ch_scenes)
        duration_min = max(1, round(duration_secs / 60))

        meta = meta_lookup.get(ch_num, {})

        start_scene = ch_scenes[0]["scene_number"] if ch_scenes else 1
        end_scene = ch_scenes[-1]["scene_number"] if ch_scenes else 1

        chapters_built.append({
            "chapter_number": ch_num,
            "title": meta.get("title", f"Capítulo {ch_num}"),
            "synopsis": meta.get("synopsis", ""),
            "duration_minutes": duration_min,
            "cliffhanger": meta.get("cliffhanger") if ch_num < num_chapters else None,
            "start_scene_number": start_scene,
            "end_scene_number": end_scene,
        })

    state["chapters"] = chapters_built
    logger.info("[ChapterSplitter] %d capítulos organizados.", len(chapters_built))
    return state
