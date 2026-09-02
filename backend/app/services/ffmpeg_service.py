"""Servicio de ensamblaje de video con FFmpeg.
Soporta videos largos, capítulos, y rutas con espacios en Windows.
"""
from __future__ import annotations

import logging
import subprocess
import shlex
import tempfile
from pathlib import Path

from backend.config import settings

logger = logging.getLogger(__name__)


class FFmpegService:
    """Ensambla escenas (imagen + audio) en videos finales con soporte de capítulos."""

    def assemble_video(
        self,
        scenes: list[dict],  # [{image_path, audio_path, duration_seconds}]
        output_path: Path,
        resolution: tuple[int, int] = (1920, 1080),
        fps: int = 24,
        platform: str = "youtube",
    ) -> Path:
        """
        Ensambla todas las escenas en un solo video.
        Cada escena es una imagen estática + audio → clip de video.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not scenes:
            logger.warning("No hay escenas para ensamblar en %s", output_path)
            return self._create_placeholder_video(output_path, resolution)

        # Determinar resolución según plataforma
        if platform in ("tiktok", "facebook", "shorts"):
            resolution = (1080, 1920)

        # Crear clips individuales y luego concatenar
        clip_paths: list[Path] = []
        for i, scene in enumerate(scenes):
            try:
                clip = self._create_clip(
                    image=Path(scene["image_path"]),
                    audio=Path(scene["audio_path"]),
                    duration=scene.get("duration_seconds", 60),
                    resolution=resolution,
                    fps=fps,
                    index=i,
                    output_base=output_path.parent,
                )
                clip_paths.append(clip)
            except Exception as e:
                logger.error("Error creando clip %d: %s", i, e)
                # Crear clip de silencio como fallback
                try:
                    silence_clip = self._create_silence_clip(
                        image=Path(scene["image_path"]),
                        duration=scene.get("duration_seconds", 60),
                        resolution=resolution,
                        fps=fps,
                        index=i,
                        output_base=output_path.parent,
                    )
                    clip_paths.append(silence_clip)
                except Exception as e2:
                    logger.error("Error creando clip de silencio %d: %s", i, e2)

        if not clip_paths:
            logger.error("No se pudo crear ningún clip. Abortando ensamblaje.")
            return self._create_placeholder_video(output_path, resolution)

        # Concatenar todos los clips
        try:
            self._concat_clips(clip_paths, output_path)
        except Exception as e:
            logger.error("Error concatenando clips: %s", e)
            # Intentar con método alternativo (input múltiple)
            self._concat_clips_filter(clip_paths, output_path)

        # Limpiar clips temporales
        for clip in clip_paths:
            if "_clip_" in clip.name or "_sclip_" in clip.name:
                clip.unlink(missing_ok=True)

        logger.info("✅ Video ensamblado: %s (%dx%d)", output_path.name, *resolution)
        return output_path

    def assemble_chapter_video(
        self,
        scenes_by_chapter: dict[int, list[dict]],
        project_dir: Path,
        platform: str = "youtube",
    ) -> dict[int, Path]:
        """Ensambla un video por capítulo. Retorna {chapter_num: video_path}."""
        chapter_videos: dict[int, Path] = {}

        for ch_num, scenes in sorted(scenes_by_chapter.items()):
            ch_dir = project_dir / f"chapter_{ch_num:02d}"
            ch_dir.mkdir(parents=True, exist_ok=True)
            ch_output = ch_dir / f"capitulo_{ch_num:02d}.mp4"

            logger.info("[FFmpeg] Ensamblando capítulo %d (%d escenas)...", ch_num, len(scenes))
            try:
                self.assemble_video(scenes, ch_output, platform=platform)
                chapter_videos[ch_num] = ch_output
            except Exception as e:
                logger.error("[FFmpeg] Error en capítulo %d: %s", ch_num, e)

        return chapter_videos

    def merge_chapter_videos(
        self,
        chapter_paths: dict[int, Path],
        output_path: Path,
        add_chapter_cards: bool = True,
    ) -> Path:
        """Une todos los capítulos en un video completo con transiciones."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        clip_paths = [chapter_paths[ch] for ch in sorted(chapter_paths.keys())]
        if not clip_paths:
            return output_path

        if len(clip_paths) == 1:
            import shutil
            shutil.copy2(clip_paths[0], output_path)
            return output_path

        # Crear archivo de concat
        self._concat_clips(clip_paths, output_path, use_copy=True)
        logger.info("✅ Video completo ensamblado: %s", output_path.name)
        return output_path

    def _create_clip(
        self,
        image: Path,
        audio: Path,
        duration: int,
        resolution: tuple[int, int],
        fps: int,
        index: int,
        output_base: Path,
    ) -> Path:
        """Crea un clip de video a partir de una imagen estática + audio."""
        clip_path = output_base / f"_clip_{index:04d}.mp4"
        if clip_path.exists() and clip_path.stat().st_size > 1000:
            return clip_path

        w, h = resolution
        # Filtro de escala con relleno negro (compatible con todas las proporciones)
        scale_filter = (
            f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black"
        )

        # Añadir efecto de zoom sutil (Ken Burns effect) para anime
        zoom_filter = (
            f"zoompan=z='min(zoom+0.0004,1.08)':d={duration * fps}:s={w}x{h}"
        )

        # Usar escala simple si Ken Burns falla (más compatible)
        cmd = [
            settings.ffmpeg_path, "-y",
            "-loop", "1",
            "-i", str(image),
            "-i", str(audio),
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-vf", scale_filter,
            "-r", str(fps),
            "-t", str(duration),
            "-shortest",
            "-pix_fmt", "yuv420p",
            str(clip_path),
        ]
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            timeout=max(60, duration * 3),
        )
        return clip_path

    def _create_silence_clip(
        self,
        image: Path,
        duration: int,
        resolution: tuple[int, int],
        fps: int,
        index: int,
        output_base: Path,
    ) -> Path:
        """Crea un clip de video con imagen y silencio (sin audio)."""
        clip_path = output_base / f"_sclip_{index:04d}.mp4"
        w, h = resolution
        scale_filter = (
            f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black"
        )
        cmd = [
            settings.ffmpeg_path, "-y",
            "-loop", "1",
            "-i", str(image),
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "128k",
            "-vf", scale_filter,
            "-r", str(fps),
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            str(clip_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=max(60, duration * 3))
        return clip_path

    def _concat_clips(
        self,
        clip_paths: list[Path],
        output_path: Path,
        use_copy: bool = False,
    ) -> None:
        """Concatena clips usando el método de archivo de lista (más estable)."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            concat_file = Path(f.name)
            for clip in clip_paths:
                # En Windows, usar forward slashes y escapar apóstrofes
                safe_path = clip.absolute().as_posix().replace("'", "\\'")
                f.write(f"file '{safe_path}'\n")

        codec_args = ["-c", "copy"] if use_copy else [
            "-c:v", "libx264", "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
        ]

        cmd = [
            settings.ffmpeg_path, "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
        ] + codec_args + [str(output_path)]

        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                timeout=3600,  # 1 hora para videos muy largos
            )
        finally:
            concat_file.unlink(missing_ok=True)

    def _concat_clips_filter(self, clip_paths: list[Path], output_path: Path) -> None:
        """Concatena usando filtergraph de FFmpeg (alternativa cuando concat falla)."""
        if len(clip_paths) > 50:
            # Demasiados clips para filtergraph; dividir en lotes
            batch_size = 20
            batches = [clip_paths[i:i+batch_size] for i in range(0, len(clip_paths), batch_size)]
            batch_outputs = []

            for i, batch in enumerate(batches):
                batch_out = output_path.parent / f"_batch_{i:04d}.mp4"
                self._concat_clips_filter(batch, batch_out)
                batch_outputs.append(batch_out)

            self._concat_clips(batch_outputs, output_path, use_copy=True)
            for bo in batch_outputs:
                bo.unlink(missing_ok=True)
            return

        inputs = []
        for clip in clip_paths:
            inputs.extend(["-i", str(clip)])

        n = len(clip_paths)
        filter_complex = "".join(f"[{i}:v][{i}:a]" for i in range(n))
        filter_complex += f"concat=n={n}:v=1:a=1[outv][outa]"

        cmd = [
            settings.ffmpeg_path, "-y",
        ] + inputs + [
            "-filter_complex", filter_complex,
            "-map", "[outv]", "-map", "[outa]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            str(output_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=3600)

    def generate_short(
        self,
        scenes: list[dict],
        start: int,
        end: int,
        output_path: Path,
    ) -> Path:
        """Genera un corto vertical recortando escenas del proyecto."""
        short_scenes = scenes[start:end]
        return self.assemble_video(short_scenes, output_path, platform="shorts")

    def create_thumbnail(
        self,
        image_path: Path,
        output_path: Path,
        title: str = "",
    ) -> Path:
        """Crea una miniatura con título superpuesto (si ffmpeg lo soporta)."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Comando básico de escalado (siempre funciona)
        cmd = [
            settings.ffmpeg_path, "-y",
            "-i", str(image_path),
            "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=black",
            str(output_path),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
        except Exception as e:
            logger.warning("Error creando miniatura: %s. Copiando imagen original.", e)
            import shutil
            shutil.copy2(image_path, output_path)

        return output_path

    def _create_placeholder_video(
        self,
        output_path: Path,
        resolution: tuple[int, int] = (1920, 1080),
    ) -> Path:
        """Crea un video de placeholder cuando no hay escenas."""
        w, h = resolution
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            settings.ffmpeg_path, "-y",
            "-f", "lavfi",
            "-i", f"color=c=black:size={w}x{h}:rate=24",
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-t", "10",
            "-c:v", "libx264", "-c:a", "aac",
            str(output_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=60)
        return output_path


ffmpeg_service = FFmpegService()