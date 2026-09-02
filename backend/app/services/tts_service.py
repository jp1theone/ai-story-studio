"""Servicio de síntesis de voz con múltiples fallbacks.
Jerarquía: F5-TTS → gTTS (online) → pyttsx3 → Silencio FFmpeg
"""
from __future__ import annotations

import logging
import subprocess
import time
from pathlib import Path

from backend.config import settings

logger = logging.getLogger(__name__)


class TTSService:
    """Wrapper de TTS multi-engine con fallback automático."""

    def __init__(self) -> None:
        self.model_path = settings.tts_model_path
        self._loaded = False
        self._infer = None
        self._engine_used = "none"

    def load_model(self) -> None:
        """Intenta cargar F5-TTS. Si falla, funciona en modo fallback."""
        if self._loaded:
            return
        logger.info("Intentando cargar modelo TTS: %s", self.model_path)
        try:
            from f5_tts.infer_utils import InferConsole
            self._infer = InferConsole()
            self._loaded = True
            self._engine_used = "f5tts"
            logger.info("✅ F5-TTS cargado correctamente.")
        except ImportError:
            logger.warning("⚠️ F5-TTS no disponible. Usando motores alternativos.")
            self._loaded = False
            self._engine_used = "fallback"
        except Exception as e:
            logger.warning("⚠️ Error al cargar F5-TTS (%s). Usando motores alternativos.", e)
            self._loaded = False
            self._engine_used = "fallback"

    def unload_model(self) -> None:
        """Descarga el modelo de memoria."""
        self._loaded = False
        self._infer = None
        logger.info("Modelo TTS descargado.")

    def generate_speech(
        self,
        text: str,
        output_path: Path,
        voice_type: str = "neutral",
        reference_audio: Path | None = None,
    ) -> Path:
        """Genera audio narrado con el mejor motor disponible."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Limpiar y preparar el texto
        text = _clean_text_for_tts(text)
        if not text.strip():
            text = "Escena sin narración."

        # Intentar motores en orden de calidad
        if self._loaded and self._infer is not None:
            try:
                return self._generate_f5tts(text, output_path, reference_audio)
            except Exception as e:
                logger.warning("F5-TTS falló en esta escena (%s). Probando alternativa.", e)

        # gTTS (Google TTS, requiere internet)
        try:
            return self._generate_gtts(text, output_path, voice_type)
        except Exception as e:
            logger.warning("gTTS falló (%s). Probando pyttsx3.", e)

        # pyttsx3 (offline, baja calidad)
        try:
            return self._generate_pyttsx3(text, output_path, voice_type)
        except Exception as e:
            logger.warning("pyttsx3 falló (%s). Generando silencio.", e)

        # Último recurso: silencio con la duración correcta
        return self._generate_silence(output_path, _estimate_duration(text))

    def _generate_f5tts(self, text: str, output_path: Path, ref: Path | None) -> Path:
        """Genera con F5-TTS."""
        # Dividir textos muy largos en chunks
        chunks = _split_text_chunks(text, max_chars=500)
        if len(chunks) == 1:
            cmd = [
                "python", "-m", "f5_tts.infer_cli",
                "--model", str(self.model_path),
                "--text", text,
                "--output", str(output_path),
            ]
            if ref:
                cmd.extend(["--ref_audio", str(ref)])
            result = subprocess.run(cmd, check=True, capture_output=True, timeout=300)
            return output_path
        else:
            # Generar chunks y concatenar
            chunk_paths = []
            for i, chunk in enumerate(chunks):
                chunk_path = output_path.parent / f"_chunk_{output_path.stem}_{i}.wav"
                cmd = [
                    "python", "-m", "f5_tts.infer_cli",
                    "--model", str(self.model_path),
                    "--text", chunk,
                    "--output", str(chunk_path),
                ]
                subprocess.run(cmd, check=True, capture_output=True, timeout=300)
                chunk_paths.append(chunk_path)
            return _concat_audio_files(chunk_paths, output_path)

    def _generate_gtts(self, text: str, output_path: Path, voice_type: str) -> Path:
        """Genera con Google TTS (requiere internet)."""
        from gtts import gTTS
        lang = "es"
        slow = False

        # Dividir si el texto es muy largo (gTTS tiene límite)
        chunks = _split_text_chunks(text, max_chars=2000)
        chunk_paths = []

        for i, chunk in enumerate(chunks):
            chunk_path = output_path.parent / f"_gtts_{output_path.stem}_{i}.mp3"
            tts = gTTS(text=chunk, lang=lang, slow=slow)
            tts.save(str(chunk_path))
            chunk_paths.append(chunk_path)

        if len(chunk_paths) == 1:
            # Convertir mp3 a wav
            _convert_to_wav(chunk_paths[0], output_path)
            chunk_paths[0].unlink(missing_ok=True)
        else:
            # Concatenar y convertir
            mp3_concat = output_path.parent / f"_gtts_concat_{output_path.stem}.mp3"
            _concat_audio_files(chunk_paths, mp3_concat, fmt="mp3")
            _convert_to_wav(mp3_concat, output_path)
            mp3_concat.unlink(missing_ok=True)
            for p in chunk_paths:
                p.unlink(missing_ok=True)

        logger.info("✅ Audio generado con gTTS: %s", output_path.name)
        return output_path

    def _generate_pyttsx3(self, text: str, output_path: Path, voice_type: str) -> Path:
        """Genera con pyttsx3 (offline)."""
        import pyttsx3
        engine = pyttsx3.init()

        # Ajustar velocidad por tipo de voz
        rate = engine.getProperty("rate")
        if "suave" in voice_type.lower():
            engine.setProperty("rate", int(rate * 0.85))
        elif "ronca" in voice_type.lower() or "profunda" in voice_type.lower():
            engine.setProperty("rate", int(rate * 0.9))

        # Guardar a WAV
        wav_path = output_path.with_suffix(".wav")
        engine.save_to_file(text, str(wav_path))
        engine.runAndWait()
        engine.stop()

        # Verificar que se generó
        if wav_path.exists() and wav_path.stat().st_size > 1000:
            if wav_path != output_path:
                wav_path.rename(output_path)
            logger.info("✅ Audio generado con pyttsx3: %s", output_path.name)
            return output_path

        raise RuntimeError("pyttsx3 generó archivo vacío o inválido.")

    def _generate_silence(self, output_path: Path, duration_seconds: float) -> Path:
        """Genera silencio con FFmpeg como último recurso."""
        logger.warning("⚠️ Generando silencio de %.1fs para %s", duration_seconds, output_path.name)
        duration_seconds = max(5.0, duration_seconds)
        cmd = [
            settings.ffmpeg_path,
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo",
            "-t", str(duration_seconds),
            "-y",
            str(output_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=60)
        return output_path


def _clean_text_for_tts(text: str) -> str:
    """Limpia el texto para síntesis de voz."""
    import re
    # Eliminar markdown
    text = re.sub(r"\*\*?(.*?)\*\*?", r"\1", text)
    text = re.sub(r"__?(.*?)__?", r"\1", text)
    # Convertir guiones de diálogo a pausa natural
    text = text.replace("—", ". ")
    text = text.replace("–", ". ")
    # Eliminar caracteres especiales que confunden al TTS
    text = re.sub(r"[*#\[\]{}\\|<>]", "", text)
    # Normalizar espacios
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _estimate_duration(text: str) -> float:
    """Estima la duración del audio basada en el número de palabras."""
    words = len(text.split())
    return max(5.0, words / 2.5)  # ~150 palabras por minuto


def _split_text_chunks(text: str, max_chars: int = 500) -> list[str]:
    """Divide el texto en chunks respetando oraciones."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    sentences = text.replace(".\n", ". ").split(". ")
    current = ""

    for sentence in sentences:
        test = current + sentence + ". "
        if len(test) > max_chars and current:
            chunks.append(current.strip())
            current = sentence + ". "
        else:
            current = test

    if current.strip():
        chunks.append(current.strip())

    return chunks or [text[:max_chars]]


def _concat_audio_files(paths: list[Path], output: Path, fmt: str = "wav") -> Path:
    """Concatena archivos de audio con FFmpeg."""
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        concat_path = Path(f.name)
        for p in paths:
            # Escapar apóstrofes en rutas
            safe_path = str(p.absolute()).replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")

    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        settings.ffmpeg_path, "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_path),
        "-c", "copy",
        str(output),
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=120)
    concat_path.unlink(missing_ok=True)

    # Limpiar chunks temporales
    for p in paths:
        if "_chunk_" in p.name or "_gtts_" in p.name:
            p.unlink(missing_ok=True)

    return output


def _convert_to_wav(src: Path, dst: Path) -> Path:
    """Convierte un audio a WAV con FFmpeg."""
    cmd = [
        settings.ffmpeg_path, "-y",
        "-i", str(src),
        "-ar", "44100", "-ac", "2",
        str(dst),
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=120)
    return dst


tts_service = TTSService()