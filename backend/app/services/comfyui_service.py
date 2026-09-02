"""Servicio de integración con ComfyUI para generación de imágenes reales."""
from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)

# Proceso ComfyUI gestionado por este servicio
_comfyui_process: subprocess.Popen | None = None


class ComfyUIService:
    """Cliente async para la API de ComfyUI."""

    def __init__(self) -> None:
        self.base_url = settings.comfyui_url
        self.client = httpx.AsyncClient(timeout=300.0)

    # ── Auto-inicio de ComfyUI ──────────────────────────────────────────────

    async def ensure_running(self) -> None:
        """Verifica que ComfyUI esté respondiendo; si no, lo inicia y espera."""
        if await self._is_alive():
            logger.info("ComfyUI ya está activo en %s", self.base_url)
            return

        logger.info("ComfyUI no responde — iniciando proceso local...")
        await self._start_process()

        # Esperar hasta 120 segundos a que ComfyUI arranque
        for attempt in range(60):
            await asyncio.sleep(2.0)
            if await self._is_alive():
                logger.info("ComfyUI listo tras %ds", (attempt + 1) * 2)
                return
            logger.debug("Esperando ComfyUI... intento %d/60", attempt + 1)

        raise RuntimeError(
            "ComfyUI no respondió en 120 segundos. "
            "Revisa comfyui/comfyui.log para más detalles."
        )

    async def _is_alive(self) -> bool:
        """Devuelve True si ComfyUI responde al health check."""
        try:
            r = await self.client.get(f"{self.base_url}/system_stats", timeout=3.0)
            return r.status_code == 200
        except Exception:
            return False

    async def _start_process(self) -> None:
        """Lanza el proceso ComfyUI en segundo plano."""
        global _comfyui_process
        if _comfyui_process and _comfyui_process.poll() is None:
            logger.info("Proceso ComfyUI ya existe (PID %d)", _comfyui_process.pid)
            return

        comfy_python = (
            Path(settings.comfyui_workflow_dir).parent
            / "ComfyUI" / ".venv" / "Scripts" / "python.exe"
        )
        comfy_main = (
            Path(settings.comfyui_workflow_dir).parent
            / "ComfyUI" / "main.py"
        )

        if not comfy_python.exists() or not comfy_main.exists():
            raise FileNotFoundError(
                f"ComfyUI no está instalado. Rutas esperadas:\n"
                f"  Python: {comfy_python}\n"
                f"  Main:   {comfy_main}"
            )

        log_path = Path(settings.comfyui_workflow_dir).parent / "comfyui.log"
        log_file = open(log_path, "a", encoding="utf-8")
        _comfyui_process = subprocess.Popen(
            [str(comfy_python), str(comfy_main), "--listen", "127.0.0.1", "--port", "8188"],
            cwd=str(comfy_main.parent),
            stdout=log_file,
            stderr=log_file,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )
        logger.info("ComfyUI iniciado: PID %d — log en %s", _comfyui_process.pid, log_path)

    # ── Generación de imágenes ──────────────────────────────────────────────

    async def generate_image(
        self,
        prompt_text: str,
        style: str,
        character_refs: list[str] | None = None,
        seed: int | None = None,
        output_dir: Path | None = None,
    ) -> Path:
        """Garantiza que ComfyUI está corriendo, genera la imagen y devuelve la ruta.

        No existe imagen de respaldo: si el motor falla se lanza RuntimeError
        para que el pipeline se detenga con un mensaje claro.
        """
        output_dir = output_dir or settings.output_dir
        try:
            # Asegurar que ComfyUI esté activo antes de cualquier petición
            await self.ensure_running()

            uploaded_refs = await self._upload_reference_images(character_refs or [])
            workflow = self._build_workflow(prompt_text, style, uploaded_refs, seed)

            # Enviar workflow a ComfyUI
            prompt_id = await self._queue_prompt(workflow)
            logger.info("ComfyUI prompt encolado: %s", prompt_id)

            # Esperar a que termine
            output_path = await self._wait_for_result(prompt_id, output_dir)
            logger.info("Imagen generada: %s", output_path)
            return output_path
        except Exception as e:
            logger.exception("ComfyUI no pudo generar la imagen: %s", e)
            raise RuntimeError(
                f"El motor visual ComfyUI falló al generar la imagen: {e}. "
                "Revisa http://127.0.0.1:8188 y logs/comfyui/comfyui.log."
            ) from e

    async def _upload_reference_images(self, reference_paths: list[str]) -> list[str]:
        """Carga las fichas del proyecto a ComfyUI para IP-Adapter.

        ComfyUI trabaja con su directorio ``input``. La carga explícita evita
        rutas del disco dependientes del navegador y permite que cada escena
        use la misma ficha visual del personaje.
        """
        uploaded: list[str] = []
        for raw_path in reference_paths:
            path = Path(raw_path)
            if not path.is_file():
                raise FileNotFoundError(f"Ficha visual no encontrada: {path}")
            filename = f"ai_story_ref_{uuid4().hex[:12]}_{path.name}"
            with path.open("rb") as image_file:
                response = await self.client.post(
                    f"{self.base_url}/upload/image",
                    files={"image": (filename, image_file, "image/jpeg")},
                    data={"overwrite": "true"},
                )
            response.raise_for_status()
            uploaded.append(response.json().get("name", filename))
        return uploaded

    def _generate_anime_placeholder(
        self, prompt_text: str, style: str, output_dir: Path
    ) -> Path:
        """Genera un placeholder estilizado de anime con gradientes y efectos."""
        try:
            from PIL import Image, ImageDraw, ImageFilter
        except ImportError:
            logger.error("Pillow no disponible. No se puede generar placeholder.")
            raise

        import hashlib
        import random
        import colorsys
        import math

        output_dir.mkdir(parents=True, exist_ok=True)
        w, h = settings.image_width, settings.image_height

        # Paletas de colores por estilo de anime
        style_palettes = {
            "anime": [(240, 100, 0.6), (280, 80, 0.5)],          # Purpura/Azul profundo
            "realista": [(210, 60, 0.3), (230, 70, 0.4)],         # Azul noche
            "manga": [(0, 0, 0.1), (220, 30, 0.3)],               # Blanco/Negro + azul
            "fantasy": [(280, 90, 0.4), (320, 80, 0.55)],         # Violeta/Magenta
            "sci-fi": [(200, 100, 0.3), (180, 90, 0.45)],         # Cian/Azul tecnológico
            "dark": [(0, 0, 0.05), (240, 80, 0.15)],              # Casi negro
            "horror": [(350, 70, 0.2), (0, 100, 0.25)],           # Rojo oscuro
        }

        palette = style_palettes.get(style.lower(), style_palettes["anime"])
        h1, s1, v1 = palette[0]
        h2, s2, v2 = palette[1]

        # La escena debe tener una identidad visual repetible: el mismo guion
        # genera siempre la misma paleta y composición, en vez de un fondo al
        # azar que no guarda relación entre una escena y otra.
        seed = int(hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()[:8], 16)
        rng = random.Random(seed)
        prompt_lower = prompt_text.lower()
        if any(word in prompt_lower for word in ("bosque", "árbol", "naturaleza", "selva")):
            palette = [(145, 55, 0.24), (105, 50, 0.38)]
        elif any(word in prompt_lower for word in ("ciudad", "neón", "edificio", "calle")):
            palette = [(220, 75, 0.27), (285, 75, 0.42)]
        elif any(word in prompt_lower for word in ("batalla", "lucha", "guerra", "ataque")):
            palette = [(8, 85, 0.36), (35, 90, 0.58)]
        elif any(word in prompt_lower for word in ("noche", "sombra", "misterio", "terror")):
            palette = [(235, 65, 0.13), (270, 72, 0.29)]

        hue_shift = rng.randint(-20, 20)
        h1 = (h1 + hue_shift) % 360
        h2 = (h2 + hue_shift) % 360

        # Convertir HSV a RGB
        def hsv_to_rgb(h, s, v):
            return tuple(int(x * 255) for x in colorsys.hsv_to_rgb(h/360, s/100, v))

        color1 = hsv_to_rgb(h1, s1, v1)
        color2 = hsv_to_rgb(h2, s2, v2)

        # Crear imagen base con gradiente
        img = Image.new("RGB", (w, h), color1)
        draw = ImageDraw.Draw(img)

        # Gradiente vertical
        for y in range(h):
            t = y / h
            r = int(color1[0] * (1 - t) + color2[0] * t)
            g = int(color1[1] * (1 - t) + color2[1] * t)
            b = int(color1[2] * (1 - t) + color2[2] * t)
            draw.line([(0, y), (w, y)], fill=(r, g, b))

        # ── Efectos decorativos estilo anime ──

        # 1. Partículas brillantes (efecto sakura/polvo estelar)
        light_color = tuple(min(255, c + 120) for c in color2)
        for _ in range(80):
            x = rng.randint(0, w)
            y = rng.randint(0, h)
            size = rng.randint(2, 8)
            alpha_factor = rng.uniform(0.3, 1.0)
            particle_color = tuple(int(c * alpha_factor) for c in light_color)
            draw.ellipse([x-size, y-size, x+size, y+size], fill=particle_color)

        # 2. Líneas de velocidad / energía (estilo shonen)
        energy_color = tuple(min(255, c + 80) for c in color1)
        center_x, center_y = w // 2, h // 2
        for angle in range(0, 360, rng.randint(8, 20)):
            rad = math.radians(angle)
            start_r = rng.randint(100, 200)
            end_r = rng.randint(300, w)
            x1 = int(center_x + start_r * math.cos(rad))
            y1 = int(center_y + start_r * math.sin(rad))
            x2 = int(center_x + end_r * math.cos(rad))
            y2 = int(center_y + end_r * math.sin(rad))
            draw.line([(x1, y1), (x2, y2)], fill=energy_color, width=1)

        # 3. Círculo central (efecto de portal/aura)
        aura_color = tuple(min(255, c + 60) for c in light_color)
        for radius in range(80, 200, 15):
            opacity = max(20, int(180 - radius * 0.7))
            r_c = min(255, aura_color[0])
            g_c = min(255, aura_color[1])
            b_c = min(255, aura_color[2])
            draw.ellipse(
                [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                outline=(r_c, g_c, b_c),
                width=2,
            )

        # Siluetas de personajes y un rótulo de escena: composición narrativa
        # útil cuando no hay un modelo de difusión disponible.
        figure_color = tuple(max(0, c - 65) for c in color1)
        figure_count = 2 if any(word in prompt_lower for word in ("dos", "pareja", "con", "personajes")) else 1
        for idx in range(figure_count):
            x = int(w * (0.38 + idx * 0.24))
            draw.ellipse([x - 48, int(h * .38), x + 48, int(h * .38) + 96], fill=figure_color)
            draw.polygon([(x - 92, int(h * .82)), (x + 92, int(h * .82)), (x, int(h * .47))], fill=figure_color)

        # 4. Marco estilo anime (borde decorativo)
        border_color = tuple(min(255, c + 40) for c in aura_color)
        draw.rectangle([0, 0, w-1, h-1], outline=border_color, width=8)
        draw.rectangle([15, 15, w-16, h-16], outline=border_color, width=2)

        # 5. Aplicar blur suave para dar profundidad
        img = img.filter(ImageFilter.GaussianBlur(radius=1))

        # 6. Texto del estilo en la esquina (marca de agua sutil)
        try:
            label_color = tuple(min(255, c + 100) for c in color2)
            draw2 = ImageDraw.Draw(img)
            caption = " ".join(prompt_text.replace("\n", " ").split()[:12])
            draw2.rectangle([16, h - 94, w - 16, h - 16], fill=tuple(max(0, c - 80) for c in color1))
            draw2.text((28, h - 78), caption[:110], fill=label_color)
            draw2.text((28, h - 42), f"AI Story Studio · {style.upper()}", fill=label_color)
        except Exception:
            pass

        # Guardar
        dest = output_dir / f"scene_{uuid4().hex[:12]}.jpg"
        img.save(dest, "JPEG", quality=95)
        logger.info("🎨 Placeholder anime generado: %s", dest.name)
        return dest

    def _build_workflow(
        self,
        prompt_text: str,
        style: str,
        character_refs: list[str] | None,
        seed: int | None,
    ) -> dict[str, Any]:
        """Construye el workflow de ComfyUI según el estilo."""
        workflow_path = settings.comfyui_workflow_dir / f"{style}.json"
        if not workflow_path.exists():
            workflow_path = settings.comfyui_workflow_dir / "anime.json"

        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow = json.load(f)

        # ── Detectar el nodo CLIPTextEncode positivo correctamente ──────────
        # Los IDs de nodo son numéricos ("1", "2", "3"...), no contienen "positive".
        # El KSampler indica su nodo positivo en inputs.positive = ["<id>", 0].
        # Se extrae esa referencia para inyectar el prompt en el nodo correcto.
        positive_node_id: str | None = None
        negative_node_id: str | None = None
        for node_id, node in workflow.items():
            if node.get("class_type") == "KSampler":
                pos_ref = node.get("inputs", {}).get("positive")
                neg_ref = node.get("inputs", {}).get("negative")
                if isinstance(pos_ref, list) and pos_ref:
                    positive_node_id = str(pos_ref[0])
                if isinstance(neg_ref, list) and neg_ref:
                    negative_node_id = str(neg_ref[0])
                break

        if positive_node_id and positive_node_id in workflow:
            # Anteponer el prompt del usuario a las etiquetas de calidad existentes.
            # Animagine XL funciona mejor cuando el contenido va primero y las
            # etiquetas de calidad van al final del prompt positivo.
            existing_quality_tags = workflow[positive_node_id]["inputs"].get("text", "")
            combined_prompt = f"{prompt_text}, {existing_quality_tags}" if existing_quality_tags else prompt_text
            workflow[positive_node_id]["inputs"]["text"] = combined_prompt
            logger.debug("Prompt inyectado en nodo %s (positivo)", positive_node_id)
        else:
            # Fallback: primer CLIPTextEncode encontrado
            for node_id, node in workflow.items():
                if node.get("class_type") == "CLIPTextEncode":
                    node["inputs"]["text"] = prompt_text
                    logger.warning(
                        "No se encontró nodo positivo por referencia KSampler; "
                        "usando primer CLIPTextEncode: %s", node_id
                    )
                    break

        # Mantener una semilla de identidad entre retrato y escena. El prompt
        # sigue describiendo la acción; la semilla evita que el modelo vuelva a
        # inventar por completo el rostro en cada imagen.
        if seed is not None:
            for node in workflow.values():
                if node.get("class_type") == "KSampler":
                    node.setdefault("inputs", {})["seed"] = int(seed) % 2_147_483_647

        # Anclar los personajes a las fichas visuales con IP-Adapter. Cada
        # referencia se aplica sobre el modelo de forma secuencial: esto permite
        # una pareja MC/FMC sin fusionar sus rostros en una sola referencia.
        if character_refs:
            checkpoint_node = next(
                node_id
                for node_id, node in workflow.items()
                if node.get("class_type") == "CheckpointLoaderSimple"
            )
            sampler_node = next(
                node_id
                for node_id, node in workflow.items()
                if node.get("class_type") == "KSampler"
            )
            loader_id = "ipadapter_loader"
            workflow[loader_id] = {
                "class_type": "IPAdapterUnifiedLoader",
                "inputs": {
                    "model": [checkpoint_node, 0],
                    "preset": "PLUS (high strength)",
                },
            }
            previous_model: list[str | int] = [loader_id, 0]
            for index, filename in enumerate(character_refs):
                image_id = f"character_reference_{index}"
                apply_id = f"ipadapter_apply_{index}"
                workflow[image_id] = {
                    "class_type": "LoadImage",
                    "inputs": {"image": filename},
                }
                workflow[apply_id] = {
                    "class_type": "IPAdapterAdvanced",
                    "inputs": {
                        "model": previous_model,
                        "ipadapter": [loader_id, 1],
                        "image": [image_id, 0],
                        "weight": 0.62,
                        "weight_type": "linear",
                        "combine_embeds": "average",
                        "start_at": 0.0,
                        "end_at": 0.85,
                        "embeds_scaling": "K+mean(V) w/ C penalty",
                    },
                }
                previous_model = [apply_id, 0]
            workflow[sampler_node]["inputs"]["model"] = previous_model
            logger.info("IP-Adapter anclado a %d fichas visuales", len(character_refs))

        return workflow

    async def _queue_prompt(self, workflow: dict) -> str:
        """Encola un workflow en ComfyUI y devuelve el prompt_id."""
        resp = await self.client.post(
            f"{self.base_url}/prompt",
            json={"prompt": workflow, "client_id": str(uuid4())},
        )
        resp.raise_for_status()
        return resp.json()["prompt_id"]

    async def _wait_for_result(self, prompt_id: str, output_dir: Path) -> Path:
        """Espera a que ComfyUI termine y copia la imagen de salida."""
        import asyncio

        output_dir.mkdir(parents=True, exist_ok=True)

        max_wait = 300  # 5 minutos máximo
        elapsed = 0
        while elapsed < max_wait:
            resp = await self.client.get(f"{self.base_url}/history/{prompt_id}")
            if resp.status_code == 200:
                history = resp.json()
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    for node_id, node_output in outputs.items():
                        if "images" in node_output:
                            filename = node_output["images"][0]["filename"]
                            subfolder = node_output["images"][0].get("subfolder", "")
                            src = (
                                settings.comfyui_workflow_dir.parent
                                / "ComfyUI" / "output" / subfolder / filename
                            )
                            dest = output_dir / f"{uuid4().hex[:8]}_{filename}"
                            import shutil
                            shutil.copy2(src, dest)
                            return dest
            await asyncio.sleep(2.0)
            elapsed += 2

        raise TimeoutError(f"ComfyUI no terminó en {max_wait}s para prompt {prompt_id}")

    async def close(self) -> None:
        await self.client.aclose()


comfyui_service = ComfyUIService()
