"""Tarea principal de generación. Orquesta el grafo de agentes y guarda en DB.
Soporte completo de capítulos, videos de 30+ minutos, y errores robustos.
"""
from __future__ import annotations

import logging
import shutil
import time
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from backend.config import settings
from backend.database import Base
from backend.app.models.project import Project, ProjectStatus, Scene, Character, Short, Chapter
from backend.app.services.ffmpeg_service import ffmpeg_service
from backend.app.api.ws import broadcast_log, broadcast_progress

logger = logging.getLogger(__name__)

# Estado global de generaciones activas (en producción usar Redis)
_active_generations: dict[int, dict] = {}


def get_status(project_id: int) -> dict | None:
    return _active_generations.get(project_id)


def _get_db() -> Session:
    """Crea una sesión DB independiente para el hilo de background."""
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
    return Session(bind=engine)


def run_full_generation(
    project_id: int,
    genres: list[str],
    style: str,
    duration_minutes: int,
    num_characters: int,
    tone: int,
    mode: str,
    prompt_text: str | None,
    platforms: list[str],
    continue_from_project_id: int | None,
    chapters_mode: bool = False,
    chapter_duration_minutes: int = 20,
) -> None:
    """Ejecuta el pipeline completo de generación en background."""
    from threading import Thread
    Thread(
        target=_run_generation_sync,
        args=(project_id, genres, style, duration_minutes, num_characters, tone,
              mode, prompt_text, platforms, continue_from_project_id,
              chapters_mode, chapter_duration_minutes),
        daemon=True,
    ).start()


def _run_generation_sync(
    project_id: int,
    genres: list[str],
    style: str,
    duration_minutes: int,
    num_characters: int,
    tone: int,
    mode: str,
    prompt_text: str | None,
    platforms: list[str],
    continue_from_project_id: int | None,
    chapters_mode: bool,
    chapter_duration_minutes: int,
) -> None:
    import asyncio
    asyncio.run(_run_generation_async(
        project_id, genres, style, duration_minutes, num_characters, tone,
        mode, prompt_text, platforms, continue_from_project_id,
        chapters_mode, chapter_duration_minutes
    ))


async def _run_generation_async(
    project_id: int,
    genres: list[str],
    style: str,
    duration_minutes: int,
    num_characters: int,
    tone: int,
    mode: str,
    prompt_text: str | None,
    platforms: list[str],
    continue_from_project_id: int | None,
    chapters_mode: bool,
    chapter_duration_minutes: int,
) -> None:
    from backend.app.agents.writer import run_writer
    from backend.app.agents.editor import run_editor
    from backend.app.agents.storyboard import run_storyboard
    from backend.app.agents.character_designer import run_character_designer
    from backend.app.agents.visual_director import run_visual_director
    from backend.app.agents.image_generator import run_image_generator
    from backend.app.agents.voice_generator import run_voice_generator
    from backend.app.agents.seo_generator import run_seo_generator
    from backend.app.agents.qa import run_qa
    from backend.app.agents.chapter_splitter import run_chapter_splitter

    db = _get_db()
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return

    # Inicializar estado
    _active_generations[project_id] = {
        "project_id": project_id,
        "phase": "generating",
        "current_agent_index": 0,
        "progress": 0,
        "scenes_generated": 0,
        "total_scenes": 0,
        "current_chapter": 0,
        "total_chapters": 1,
        "log": [],
        "error": None,
    }

    try:
        # Obtener sinopsis previa si es continuación
        prev_synopsis = None
        if mode == "continue" and continue_from_project_id:
            prev = db.query(Project).filter(Project.id == continue_from_project_id).first()
            if prev:
                prev_synopsis = prev.synopsis

        # Construir estado inicial
        state: dict[str, Any] = {
            "project_id": project_id,
            "genres": genres,
            "style": style,
            "duration_minutes": duration_minutes,
            "num_characters": num_characters,
            "tone": tone,
            "mode": mode,
            "prompt_text": prompt_text,
            "platforms": platforms,
            "prev_synopsis": prev_synopsis,
            "chapters_mode": chapters_mode,
            "chapter_duration_minutes": chapter_duration_minutes,
        }

        # Pipeline de agentes (con chapter_splitter tras writer)
        agents_pipeline = [
            ("Guionista", run_writer),
            ("Divisor Capítulos", run_chapter_splitter),
            ("Editor", run_editor),
            ("Storyboard", run_storyboard),
            ("Diseñador Chars", run_character_designer),
            ("Director Visual", run_visual_director),
            ("Gen. Imágenes", run_image_generator),
            ("Gen. Voces", run_voice_generator),
            ("SEO", run_seo_generator),
            ("QA", run_qa),
        ]

        # Los agentes críticos (imágenes) deben detener el pipeline si fallan.
        # Los agentes no-críticos (SEO, QA, Editor) pueden continuar con error.
        CRITICAL_AGENTS = {"Gen. Imágenes", "Guionista", "Gen. Voces"}
        for i, (name, agent_func) in enumerate(agents_pipeline):
            _active_generations[project_id]["current_agent_index"] = i
            broadcast_log(project_id, name, f"🚀 Iniciando {name}...", "info")
            broadcast_progress(project_id, i, int((i / len(agents_pipeline)) * 85))

            try:
                state = await agent_func(state)
            except Exception as agent_err:
                logger.error("[%s] Error en agente: %s", name, agent_err)
                if name in CRITICAL_AGENTS:
                    broadcast_log(project_id, name, f"❌ Error crítico en {name}: {agent_err}", "error")
                    raise RuntimeError(f"Agente crítico '{name}' falló: {agent_err}") from agent_err
                broadcast_log(project_id, name, f"⚠️ Error en {name}: {agent_err}. Continuando...", "warning")

            # Sin guion no hay escenas, audio ni video que generar. Antes se
            # continuaba silenciosamente y se guardaba un proyecto "completado"
            # pero vacío.
            if i == 0 and not state.get("scenes"):
                raise RuntimeError("El guionista no generó escenas; no se puede producir el video.")

            # Actualizar contadores de escenas y capítulos
            total_sc = len(state.get("scenes", []))
            num_ch = state.get("num_chapters", 1)
            _active_generations[project_id]["total_scenes"] = total_sc
            _active_generations[project_id]["total_chapters"] = num_ch

            _active_generations[project_id]["progress"] = int(((i + 1) / len(agents_pipeline)) * 85)
            broadcast_log(project_id, name, f"✅ {name} completado.", "success")
            broadcast_progress(
                project_id, i,
                int(((i + 1) / len(agents_pipeline)) * 85),
                total_scenes=total_sc,
                total_chapters=num_ch,
            )

        # ── Guardar en DB ──────────────────────────────────
        broadcast_log(project_id, "Sistema", "💾 Guardando proyecto en base de datos...", "info")

        project.title = state.get("title", "Sin título")
        project.synopsis = state.get("synopsis", "")
        project.seo_data = state.get("seo_data")
        project.thumbnail_scene_id = state.get("thumbnail_scene_id")
        project.chapters_mode = state.get("use_chapters", False)
        project.chapter_duration_minutes = state.get("chapter_duration_minutes", 20)
        project.total_chapters = state.get("num_chapters", 1)
        db.commit()

        # Guardar personajes
        for char_data in state.get("characters", []):
            char = Character(
                project_id=project_id,
                name=char_data.get("name", "Personaje"),
                role=char_data.get("role", "Secundario"),
                description=char_data.get("description", ""),
                appearance=char_data.get("appearance", ""),
                voice_type=char_data.get("voice_type", "neutral"),
                reference_image_path=char_data.get("reference_image_path"),
            )
            db.add(char)
        db.commit()

        # Guardar escenas
        for scene_data in state.get("scenes", []):
            scene = Scene(
                project_id=project_id,
                scene_number=scene_data["scene_number"],
                chapter_number=scene_data.get("chapter_number", 1),
                title=scene_data.get("title", f"Escena {scene_data['scene_number']}"),
                narration=scene_data.get("narration", ""),
                emotion=scene_data.get("emotion", "drama"),
                camera=scene_data.get("camera", "plano general"),
                image_prompt=scene_data.get("image_prompt", ""),
                duration_seconds=scene_data.get("duration_seconds", 120),
                character_names=scene_data.get("character_names", []),
                image_path=scene_data.get("image_path"),
                audio_path=scene_data.get("audio_path"),
            )
            db.add(scene)
        db.commit()

        # Guardar capítulos
        for ch_data in state.get("chapters", []):
            chapter = Chapter(
                project_id=project_id,
                chapter_number=ch_data["chapter_number"],
                title=ch_data.get("title", f"Capítulo {ch_data['chapter_number']}"),
                synopsis=ch_data.get("synopsis", ""),
                duration_minutes=ch_data.get("duration_minutes", 20),
                cliffhanger=ch_data.get("cliffhanger"),
                start_scene_number=ch_data.get("start_scene_number", 1),
                end_scene_number=ch_data.get("end_scene_number", 1),
            )
            db.add(chapter)
        db.commit()

        # ── Ensamblar videos ───────────────────────────────
        broadcast_log(project_id, "FFmpeg", "🎬 Ensamblando videos...", "info")
        _active_generations[project_id]["progress"] = 87

        scenes_all = state.get("scenes", [])
        # Se produce un MP4 para cada plataforma solicitada. Antes solo se
        # ensamblaba la primera (normalmente YouTube), aunque la interfaz
        # anunciaba exportaciones para todas las plataformas seleccionadas.
        target_platforms = list(dict.fromkeys(platforms or ["youtube"]))

        # Preparar escenas por capítulo
        scenes_by_chapter: dict[int, list[dict]] = {}
        for s in scenes_all:
            if s.get("image_path") and s.get("audio_path"):
                ch = s.get("chapter_number", 1)
                scenes_by_chapter.setdefault(ch, []).append({
                    "image_path": s["image_path"],
                    "audio_path": s["audio_path"],
                    "duration_seconds": s.get("duration_seconds", 120),
                })

        num_chapters = state.get("num_chapters", 1)
        project_dir = settings.output_dir / str(project_id)

        video_paths: list[Path] = []
        if num_chapters > 1 and len(scenes_by_chapter) > 1:
            # Ensamblar video por capítulo
            chapter_video_paths = ffmpeg_service.assemble_chapter_video(
                scenes_by_chapter,
                project_dir / "chapters",
                platform="youtube",
            )

            # Actualizar paths en DB
            for ch_num, vid_path in chapter_video_paths.items():
                ch_db = db.query(Chapter).filter(
                    Chapter.project_id == project_id,
                    Chapter.chapter_number == ch_num
                ).first()
                if ch_db:
                    ch_db.video_path = str(vid_path)
            db.commit()

            # Ensamblar video completo uniendo capítulos
            if chapter_video_paths:
                for platform in target_platforms:
                    full_output = project_dir / platform / f"{project.title[:60]}_completo.mp4"
                    full_output.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        # Los capítulos se ensamblan en horizontal; para las
                        # exportaciones verticales se crean a partir de las
                        # escenas individuales más abajo cuando es necesario.
                        if platform == "youtube":
                            ffmpeg_service.merge_chapter_videos(chapter_video_paths, full_output)
                        else:
                            platform_scenes = [s for chapter in scenes_by_chapter.values() for s in chapter]
                            ffmpeg_service.assemble_video(platform_scenes, full_output, platform=platform)
                        if full_output.is_file() and full_output.stat().st_size > 0:
                            video_paths.append(full_output)
                        broadcast_log(project_id, "FFmpeg", f"✅ Video {platform} ensamblado: {full_output.name}", "success")
                    except Exception as e:
                        logger.error("Error ensamblando video completo para %s: %s", platform, e)
                        broadcast_log(project_id, "FFmpeg", f"⚠️ Error en {platform}: {e}", "warning")

            broadcast_log(project_id, "FFmpeg", f"✅ {len(chapter_video_paths)} capítulos ensamblados.", "success")

        else:
            # Video único
            scenes_for_ffmpeg = scenes_by_chapter.get(1, [])
            if not scenes_for_ffmpeg:
                scenes_for_ffmpeg = [
                    s for ch_scenes in scenes_by_chapter.values() for s in ch_scenes
                ]

            if scenes_for_ffmpeg:
                safe_title = "".join(c for c in project.title if c.isalnum() or c in " -_")[:50] or "historia"
                for platform in target_platforms:
                    output_path = project_dir / platform / f"{safe_title}.mp4"
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        produced_video = ffmpeg_service.assemble_video(scenes_for_ffmpeg, output_path, platform=platform)
                        if produced_video.is_file() and produced_video.stat().st_size > 0:
                            video_paths.append(produced_video)
                        broadcast_log(project_id, "FFmpeg", f"✅ Video {platform} ensamblado: {output_path.name}", "success")
                    except Exception as e:
                        logger.error("Error ensamblando video para %s: %s", platform, e)
                        broadcast_log(project_id, "FFmpeg", f"⚠️ Error en {platform}: {e}", "error")

        if not video_paths:
            raise RuntimeError("No se pudo ensamblar ningún video. Revisa FFmpeg y las pistas de audio e imagen.")

        # Copiar los entregables finales a una biblioteca fácil de encontrar.
        videos_dir = settings.content_dir / "Videos"
        videos_dir.mkdir(parents=True, exist_ok=True)
        for video_path in video_paths:
            destination = videos_dir / video_path.name
            shutil.copy2(video_path, destination)
            broadcast_log(project_id, "Sistema", f"📁 Video guardado en: {destination}", "success")

        # ── Miniatura ─────────────────────────────────────
        _active_generations[project_id]["progress"] = 93
        scenes_list = state.get("scenes", [])
        thumb_scene = next(
            (s for s in scenes_list if s.get("scene_number") == state.get("thumbnail_scene_id")),
            scenes_list[0] if scenes_list else {},
        )
        if thumb_scene.get("image_path"):
            thumb_out = project_dir / "thumbnail.jpg"
            try:
                ffmpeg_service.create_thumbnail(
                    Path(thumb_scene["image_path"]),
                    thumb_out,
                    state.get("thumbnail_text", ""),
                )
                broadcast_log(project_id, "FFmpeg", "✅ Miniatura creada.", "success")
            except Exception as e:
                logger.error("Error generando miniatura: %s", e)

        # No marcar como completado hasta que exista al menos un MP4 y se haya
        # terminado el ensamblaje final.
        project.status = ProjectStatus.COMPLETED
        db.commit()
        _active_generations[project_id]["phase"] = "done"
        _active_generations[project_id]["progress"] = 100
        broadcast_progress(
            project_id,
            len(agents_pipeline),
            100,
            phase="done",
            total_chapters=num_chapters,
        )
        broadcast_log(project_id, "Sistema", "🎉 ¡Proyecto completado exitosamente!", "success")

    except Exception as e:
        logger.exception("Error en generación %d: %s", project_id, e)
        project.status = ProjectStatus.FAILED
        # Conservar el error sin requerir cambios de esquema en instalaciones
        # existentes. El detalle también llega al registro en tiempo real.
        project.synopsis = f"Error de producción: {e}"
        db.commit()
        _active_generations[project_id]["phase"] = "failed"
        _active_generations[project_id]["error"] = str(e)
        broadcast_progress(project_id, -1, _active_generations[project_id].get("progress", 0), phase="failed")
        broadcast_log(project_id, "Sistema", f"❌ Error fatal: {e}", "error")
    finally:
        db.close()


def run_shorts_generation(project_id: int) -> None:
    """Genera cortos a partir de un proyecto completado."""
    from threading import Thread
    Thread(target=_run_shorts_sync, args=(project_id,), daemon=True).start()


def _run_shorts_sync(project_id: int) -> None:
    db = _get_db()
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return

    try:
        scenes = sorted(project.scenes, key=lambda s: s.scene_number)
        if not scenes:
            broadcast_log(project_id, "Cortos", "⚠️ No hay escenas disponibles.", "warning")
            return

        n = len(scenes)
        key_moments = [
            (0, min(4, n), "El inicio que no esperabas", "Todo cambió en un solo momento..."),
            (max(0, n // 4 - 1), min(n // 4 + 3, n), "El giro que lo cambió todo", "Nunca vi esto venir..."),
            (max(0, n // 2 - 1), min(n // 2 + 3, n), "La verdad sale a la luz", "No podía creer lo que veía..."),
            (max(0, n - 4), n, "El final que te dejará sin palabras", "Nadie esperaba este final..."),
        ]

        scenes_for_ffmpeg = [
            {"image_path": s.image_path, "audio_path": s.audio_path, "duration_seconds": s.duration_seconds}
            for s in scenes
            if s.image_path and s.audio_path
        ]

        # Los cortos se entregan directamente en la biblioteca del usuario.
        shorts_dir = settings.content_dir / "Shorts"
        shorts_dir.mkdir(parents=True, exist_ok=True)

        for i, (start, end, title, hook) in enumerate(key_moments):
            broadcast_log(project_id, "Cortos", f"🎬 Generando corto {i+1}: {title}", "info")
            short_scenes = scenes_for_ffmpeg[start:end]
            if not short_scenes:
                continue

            short_path = shorts_dir / f"short_{i+1:02d}.mp4"
            try:
                ffmpeg_service.assemble_video(short_scenes, short_path, platform="shorts")

                total_dur = sum(s["duration_seconds"] for s in short_scenes)
                short = Short(
                    project_id=project_id,
                    title=title,
                    hook=hook,
                    start_scene_number=scenes[start].scene_number if start < len(scenes) else 0,
                    end_scene_number=scenes[min(end, len(scenes)) - 1].scene_number if scenes else 0,
                    duration_string=f"{total_dur // 60}:{total_dur % 60:02d}",
                    platforms=["tiktok", "facebook", "shorts"],
                    video_path=str(short_path),
                )
                db.add(short)
                db.commit()
                broadcast_log(project_id, "Cortos", f"✅ Corto {i+1} completado.", "success")
            except Exception as e:
                logger.error("Error generando corto %d: %s", i, e)
                broadcast_log(project_id, "Cortos", f"⚠️ Error en corto {i+1}: {e}", "warning")

        broadcast_progress(project_id, -1, 100, phase="shorts_done")
        broadcast_log(project_id, "Cortos", "🎉 ¡Todos los cortos generados!", "success")

    except Exception as e:
        logger.exception("Error en generación de cortos: %s", e)
        broadcast_log(project_id, "Cortos", f"❌ Error: {e}", "error")
    finally:
        db.close()
