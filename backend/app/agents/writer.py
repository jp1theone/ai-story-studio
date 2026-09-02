"""Agente Guionista: genera la historia, arcos, giros y dialogos.
Para videos largos (>25 min), genera historias con capitulos automaticamente.
"""
from __future__ import annotations

import json
import logging
import math

from backend.app.services.llm_service import generate

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────
# SYSTEM PROMPT (historia completa)
# ──────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Eres un guionista profesional especializado en historias de anime narradas para YouTube.
Tu trabajo es crear historias épicas con:
- Un gancho poderoso en los primeros 60 segundos que atrape al espectador
- Arcos narrativos complejos con subidas y bajadas de tension emocional
- Al menos 3 giros impactantes e inesperados
- Dialogos naturales, memorables y emocionalmente resonantes
- Descripciones visuales cinematograficas para cada escena
- Un mundo coherente con reglas propias
- Personajes con traumas, motivaciones y arcos de desarrollo profundos
- {chapter_info}

IMPORTANTE: Cada escena debe tener una narracion EXTENSA Y DETALLADA.
La narracion debe incluir:
- Descripcion cinematografica del ambiente y atmosfera
- Pensamientos internos del protagonista
- Dialogos entre personajes (con guiones —)
- Acciones y movimientos detallados
- Transiciones suaves entre momentos

Responde SIEMPRE en JSON valido con esta estructura exacta:
{{
  "title": "Titulo epico de la historia",
  "synopsis": "Sinopsis completa y atrapante de 4-6 oraciones",
  "world_building": "Descripcion del mundo, epoca y reglas del universo",
  "chapters": [
    {{
      "chapter_number": 1,
      "title": "Titulo del capitulo",
      "synopsis": "Sinopsis del capitulo",
      "cliffhanger": "Frase de cierre que deja al espectador con ganas de mas"
    }}
  ],
  "characters": [
    {{
      "name": "Nombre del personaje",
      "role": "Protagonista|Antagonista|Secundario|Interes Romantico|Mentor|Rival",
      "description": "Descripcion psicologica profunda, trauma de origen, motivaciones y miedos",
      "appearance": "Descripcion visual ULTRA detallada: cabello, ojos, ropa, cicatrices, accesorios. Para generacion de imagenes anime realista.",
      "voice_type": "Femenina suave|Masculina profunda|Femenina aguda|Masculina ronca|Neutra|Neutra profunda|Juvenil|Anciana"
    }}
  ],
  "scenes": [
    {{
      "scene_number": 1,
      "chapter_number": 1,
      "title": "Titulo dramatico de la escena",
      "narration": "NARRACION EXTENSA: minimo 300-500 palabras con dialogos, descripciones y pensamientos internos. El narrador cuenta la historia en tercera persona omnisciente con voz cinematografica y emotiva.",
      "emotion": "intriga|sorpresa|tension|misterio|giro|melancolia|impacto|drama|accion|tragedia|resolucion|esperanza|romance|humor|terror",
      "camera": "plano general|close-up|plano medio|contrapicado|plano detalle|plano americano|camara en mano|plano aereo|travelling|zoom dramatico",
      "character_names": ["Nombre1", "Nombre2"],
      "duration_seconds": 180
    }}
  ]
}}

REGLAS CRITICAS:
- La duracion total de TODAS las escenas debe ser AL MENOS {duration_minutes} minutos ({duration_seconds} segundos)
- Cada escena debe tener entre 250 y 600 segundos de duracion
- La narracion de cada escena debe ser SUFICIENTEMENTE LARGA para cubrir su duracion (aproximadamente 150-170 palabras por minuto)
- Los personajes deben ser consistentes en TODA la historia
- Los dialogos deben estar en ESPAÑOL
- Incluye exactamente {num_characters} personajes principales
- El estilo debe ser {style} con calidad cinematografica"""


# ──────────────────────────────────────────────────────────
# SYSTEM PROMPT para un capítulo individual
# ──────────────────────────────────────────────────────────
CHAPTER_SYSTEM_PROMPT = """Eres un guionista profesional de anime. 
Genera el capitulo {chapter_number} de {total_chapters} de la historia.

La historia ya tiene estos personajes establecidos:
{characters_summary}

Sinopsis general: {main_synopsis}

Lo que ocurrio antes (capitulos anteriores): {prev_events}

Responde SOLO en JSON:
{{
  "chapter_number": {chapter_number},
  "title": "Titulo epico del capitulo",
  "synopsis": "Sinopsis del capitulo (3-4 oraciones)",
  "cliffhanger": "Frase final que engancha al siguiente capitulo",
  "scenes": [
    {{
      "scene_number": 1,
      "chapter_number": {chapter_number},
      "title": "Titulo de la escena",
      "narration": "NARRACION EXTENSA de minimo 400 palabras con dialogos en guion, pensamientos internos, descripcion cinematografica del ambiente. El narrador debe ser dramatico y envolvente.",
      "emotion": "intriga|sorpresa|tension|misterio|giro|melancolia|impacto|drama|accion|tragedia|resolucion|esperanza|romance|terror",
      "camera": "plano general|close-up|plano medio|contrapicado|plano detalle|plano americano|camara en mano|travelling|zoom dramatico",
      "character_names": ["Nombre1"],
      "duration_seconds": 240
    }}
  ]
}}

REGLAS:
- Este capitulo debe durar al menos {chapter_duration_minutes} minutos ({chapter_duration_seconds} segundos)
- Genera suficientes escenas para cubrir esa duracion
- Cada escena: 200-360 segundos de duracion
- La narracion debe tener 150-170 palabras por MINUTO de duracion de escena
- Termina con el cliffhanger si NO es el ultimo capitulo
- El ultimo capitulo debe tener resolucion satisfactoria
"""


async def run_writer(state: dict) -> dict:
    """Ejecuta el agente guionista con soporte de capitulos."""
    logger.info("[Guionista] Iniciando generacion de historia...")

    genres = state.get("genres", [])
    style = state.get("style", "anime")
    duration = state.get("duration_minutes", 22)
    num_chars = state.get("num_characters", 3)
    tone = state.get("tone", 70)
    mode = state.get("mode", "auto")
    prompt_text = state.get("prompt_text", "")
    chapters_mode = state.get("chapters_mode", False)
    chapter_duration = state.get("chapter_duration_minutes", 20)

    tone_desc = "ligero y optimista con humor" if tone < 40 else "equilibrado con momentos oscuros y emotivos" if tone < 70 else "oscuro, intenso y psicologicamente profundo"

    # Determinar si usar capítulos
    use_chapters = chapters_mode or duration > 25
    if use_chapters:
        num_chapters = max(2, math.ceil(duration / chapter_duration))
        chapter_info = f"La historia se divide en {num_chapters} capitulos de aproximadamente {chapter_duration} minutos cada uno. Cada capitulo debe terminar con un cliffhanger."
    else:
        num_chapters = 1
        chapter_info = "La historia es un video completo de una sola parte."

    logger.info("[Guionista] Modo capitulos: %s (%d capitulos)", use_chapters, num_chapters)

    # Construir prompt del usuario
    user_prompt = f"""Genera una historia de anime EPICA con estas especificaciones:
- Generos: {', '.join(genres)}
- Estilo visual: {style} realista y cinematografico
- Duracion total: {duration} minutos
- Numero de personajes: {num_chars}
- Tono narrativo: {tone_desc}
- Numero de capitulos: {num_chapters}
- Duracion por capitulo: ~{chapter_duration} minutos
- Modo: {mode}"""

    if mode == "prompt" and prompt_text:
        user_prompt += f"\n- Idea del usuario: {prompt_text}"
    elif mode == "expand" and prompt_text:
        user_prompt += f"\n- Texto base a expandir: {prompt_text[:2000]}"
    elif mode == "continue" and state.get("prev_synopsis"):
        user_prompt += f"\n- Historia previa a continuar: {state['prev_synopsis']}"

    system = (
        SYSTEM_PROMPT
        .replace("{duration_minutes}", str(duration))
        .replace("{duration_seconds}", str(duration * 60))
        .replace("{num_characters}", str(num_chars))
        .replace("{style}", style)
        .replace("{chapter_info}", chapter_info)
    )

    # Usar más tokens para historias largas
    max_tok = min(16384, max(8192, duration * 400))
    raw = generate(user_prompt, system_prompt=system, max_tokens=max_tok)

    # Parsear JSON
    story_data = _parse_json_safe(raw, user_prompt, system)

    # Asegurar estructura mínima
    if "scenes" not in story_data:
        story_data["scenes"] = []
    if "characters" not in story_data:
        story_data["characters"] = []
    if "chapters" not in story_data:
        story_data["chapters"] = []

    # Si el LLM no generó suficientes escenas por capítulo en modo multi-capítulo,
    # generar capítulos adicionales
    if use_chapters and num_chapters > 1:
        story_data = await _ensure_chapter_coverage(
            story_data, num_chapters, chapter_duration, style, genres, tone_desc
        )

    # Validar y ajustar duración total
    _adjust_duration(story_data, duration)

    # Asegurar chapter_number en cada escena
    _assign_chapter_numbers(story_data, num_chapters, chapter_duration)

    # Guardar en estado
    state["title"] = story_data.get("title", "Historia sin título")
    state["synopsis"] = story_data.get("synopsis", "")
    state["world_building"] = story_data.get("world_building", "")
    state["characters"] = story_data["characters"]
    state["scenes"] = story_data["scenes"]
    state["chapters_meta"] = story_data.get("chapters", [])
    state["story_raw"] = story_data
    state["use_chapters"] = use_chapters
    state["num_chapters"] = num_chapters
    state["chapter_duration_minutes"] = chapter_duration

    total_duration_min = sum(s.get("duration_seconds", 0) for s in story_data["scenes"]) / 60
    logger.info(
        "[Guionista] Historia generada: '%s' — %d escenas — %.1f min — %d capítulos",
        story_data["title"], len(story_data["scenes"]), total_duration_min, num_chapters
    )
    return state


async def _ensure_chapter_coverage(
    story_data: dict,
    num_chapters: int,
    chapter_duration: int,
    style: str,
    genres: list,
    tone_desc: str,
) -> dict:
    """Si hay capítulos sin escenas suficientes, genera escenas adicionales."""
    scenes_by_chapter: dict[int, list] = {}
    for scene in story_data.get("scenes", []):
        ch = scene.get("chapter_number", 1)
        scenes_by_chapter.setdefault(ch, []).append(scene)

    total_scenes = story_data.get("scenes", [])
    global_scene_num = len(total_scenes) + 1
    characters = story_data.get("characters", [])
    char_names = [c["name"] for c in characters]
    main_synopsis = story_data.get("synopsis", "")

    for ch_num in range(1, num_chapters + 1):
        ch_scenes = scenes_by_chapter.get(ch_num, [])
        ch_duration = sum(s.get("duration_seconds", 0) for s in ch_scenes)
        needed = chapter_duration * 60

        if ch_duration < needed * 0.7:  # si tiene menos del 70% de la duración
            logger.info("[Guionista] Capítulo %d insuficiente (%ds < %ds). Generando más escenas...", ch_num, ch_duration, needed)
            
            # Encontrar el cliffhanger previo
            prev_events = "Inicio de la historia"
            if ch_num > 1:
                prev_ch_scenes = scenes_by_chapter.get(ch_num - 1, [])
                if prev_ch_scenes:
                    prev_events = prev_ch_scenes[-1].get("narration", "")[:300]

            # Calcular escenas faltantes
            missing_seconds = needed - ch_duration
            scenes_needed = max(2, missing_seconds // 240)

            # Generar escenas adicionales inline (sin llamar al LLM de nuevo para velocidad)
            emotions = ["drama", "tension", "accion", "impacto", "resolucion", "esperanza"]
            cameras = ["close-up", "plano medio", "travelling", "zoom dramatico", "plano general"]
            
            for i in range(int(scenes_needed)):
                new_scene = {
                    "scene_number": global_scene_num,
                    "chapter_number": ch_num,
                    "title": f"Capítulo {ch_num} — Momento {i+1}",
                    "narration": _generate_extended_narration(
                        ch_num, i, char_names, style, genres, tone_desc
                    ),
                    "emotion": emotions[i % len(emotions)],
                    "camera": cameras[i % len(cameras)],
                    "character_names": char_names[:2],
                    "duration_seconds": 240,
                }
                total_scenes.append(new_scene)
                scenes_by_chapter.setdefault(ch_num, []).append(new_scene)
                global_scene_num += 1

    story_data["scenes"] = total_scenes
    return story_data


def _generate_extended_narration(ch_num: int, scene_idx: int, char_names: list, style: str, genres: list, tone: str) -> str:
    """Genera una narración extensa de relleno para capítulos incompletos."""
    protagonist = char_names[0] if char_names else "el protagonista"
    antagonist = char_names[1] if len(char_names) > 1 else "las sombras del destino"
    
    templates = [
        f"""El ambiente era denso, cargado de una tensión que parecía hacer más pesado el propio aire. 
{protagonist} avanzaba lentamente, cada paso resonando en el silencio absoluto que había caído sobre ese lugar.

—Sabía que llegarías hasta aquí —murmuró una voz desde las sombras—. Eres predecible.

{protagonist} apretó los puños. Las palabras de {antagonist} siempre tenían la habilidad de clavar una daga directamente en su corazón. No porque fueran falsas, sino precisamente porque contenían una verdad que él no quería admitir.

El estilo {style} del universo se manifestaba en cada detalle: los contornos afilados de los edificios contra el cielo nocturno, las luces de neón que se reflejaban en los charcos de lluvia, la música ambiental que parecía vibrar en las paredes mismas.

—¿Predecible? —respondió {protagonist} finalmente, su voz más firme de lo que sentía—. O tal vez simplemente determinado.

Una sonrisa lenta se dibujó en el rostro de {antagonist}. Era el tipo de sonrisa que no prometía nada bueno. Los géneros de {', '.join(genres)} se mezclaban en este momento: la tensión del thriller, el peso emocional del drama, la intensidad de la confrontación inevitable.

{protagonist} pensó en todos los sacrificios que lo habían llevado hasta aquí. Cada persona que había perdido, cada decisión que había tomado. Todo convergía en este instante.

—Entonces, ¿qué vas a hacer? —preguntó {antagonist}, extendiendo los brazos como si ofreciera el mundo entero—. ¿Luchar? ¿Rendirte? ¿O por fin entender que somos dos caras de la misma moneda?

La pregunta quedó flotando en el aire. {protagonist} no tenía una respuesta fácil. Y quizás eso era lo que hacía que este momento fuera tan extraordinariamente humano.""",

        f"""La memoria golpeó a {protagonist} sin previo aviso, como siempre lo hacía: en los momentos más inopportunos, cuando la guardia estaba baja.

Recordó el día en que todo cambió. El sol se había puesto de una manera particular ese atardecer, tiñendo el cielo de un naranja que ahora le parecía casi doloroso de recordar. Él había sido diferente entonces. Más joven, más ingenuo, más esperanzador.

—¿En qué piensas? —preguntó alguien a su lado.

{protagonist} volvió al presente. La realidad del capítulo {ch_num} pesaba sobre sus hombros: las decisiones tomadas, los caminos sin retorno.

—En lo que podría haber sido —admitió con honestidad brutal.

El universo de {style} los rodeaba con su belleza peculiar: líneas limpias, colores saturados, una estética que hacía que incluso el dolor pareciera hermoso de una manera perturbadora.

Los géneros de {', '.join(genres)} habían tejido esta historia como un tapiz complejo. Cada hilo tiraba en una dirección diferente, creando una tensión que mantenía todo unido precisamente porque amenazaba con desgarrarse.

—Las cosas que podrían haber sido —respondió su acompañante con sabiduría inesperada—, son el peso más pesado que existe. Más que los errores que cometemos, más que las palabras que no decimos. Es el universo de posibilidades que cerramos con cada decisión.

{protagonist} la miró fijamente. Había algo en esas palabras que resonaba en la parte más profunda de su ser, en esa zona que rara vez dejaba ver a nadie.

—¿Cómo avanzas tú? —preguntó—. ¿Cómo sigues adelante cuando sabes lo que perdiste?

La respuesta tardó en llegar, pero cuando llegó, cambió algo fundamental en la comprensión que {protagonist} tenía del mundo."""
    ]
    return templates[scene_idx % len(templates)]


def _parse_json_safe(raw: str, user_prompt: str, system: str) -> dict:
    """Parsea JSON con reintentos y limpieza."""
    try:
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0]
        return json.loads(raw.strip())
    except json.JSONDecodeError as e:
        logger.warning("[Guionista] Error parseando JSON: %s. Intentando reparar...", e)
        # Intentar reparar JSON truncado
        repaired = _repair_json(raw)
        if repaired:
            return repaired
        # Último recurso: generar historia de emergencia
        logger.error("[Guionista] No se pudo parsear JSON. Usando historia de emergencia.")
        return _emergency_story(user_prompt)


def _repair_json(raw: str) -> dict | None:
    """Intenta reparar JSON truncado."""
    try:
        # Buscar el primer { y el último } balanceado
        start = raw.find("{")
        if start == -1:
            return None
        depth = 0
        last_valid = start
        for i, c in enumerate(raw[start:], start):
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    last_valid = i
                    break
        fragment = raw[start:last_valid + 1]
        return json.loads(fragment)
    except Exception:
        return None


def _emergency_story(user_prompt: str) -> dict:
    """Historia de emergencia cuando el LLM falla completamente."""
    from backend.app.services.llm_service import generate_mock
    mock_raw = generate_mock(user_prompt, "scenes characters")
    try:
        return json.loads(mock_raw)
    except Exception:
        return {
            "title": "La Historia del Destino",
            "synopsis": "Una épica historia de anime donde el destino pone a prueba el espíritu humano.",
            "world_building": "Un mundo donde la magia y la tecnología coexisten.",
            "chapters": [],
            "characters": [
                {"name": "Akira", "role": "Protagonista", "description": "Joven guerrero determinado",
                 "appearance": "anime style, joven de 18 años, cabello negro despeinado, ojos azul oscuro, cicatriz en la mejilla izquierda, ropa casual con chaqueta roja", "voice_type": "Masculina ronca"},
                {"name": "Yuki", "role": "Secundario", "description": "Compañera leal",
                 "appearance": "anime style, chica de 17 años, cabello plateado largo, ojos violeta, uniforme escolar modificado con detalles dorados", "voice_type": "Femenina suave"},
            ],
            "scenes": [
                {"scene_number": 1, "chapter_number": 1, "title": "El Despertar",
                 "narration": "El sol se alzaba sobre la ciudad de Nexus Prime, pintando el horizonte con tonos dorados que contrastaban violentamente con las sombras que se cernían sobre el mundo. Akira abrió los ojos. La habitación seguía siendo la misma de siempre, pero algo había cambiado en el aire, una tensión imperceptible que solo los que estaban verdaderamente despiertos podían sentir. Se incorporó lentamente, dejando que los recuerdos del sueño —o más bien de la visión— se asentaran en su mente. Un dragón negro atravesando el cielo, ciudades cayendo, y una voz que decía: «Tú eres la última esperanza». —Qué dramático —murmuró para sí mismo, aunque algo en su pecho le decía que esta vez era diferente.",
                 "emotion": "intriga", "camera": "close-up", "character_names": ["Akira"], "duration_seconds": 180},
            ]
        }


def _adjust_duration(story_data: dict, duration_minutes: int) -> None:
    """Ajusta la duración total para alcanzar el mínimo requerido."""
    total_seconds = sum(s.get("duration_seconds", 0) for s in story_data.get("scenes", []))
    min_seconds = duration_minutes * 60
    if total_seconds < min_seconds:
        logger.warning("[Guionista] Duración insuficiente (%ds < %ds), ajustando...", total_seconds, min_seconds)
        deficit = min_seconds - total_seconds
        scenes = story_data["scenes"]
        if scenes:
            per_scene = deficit // len(scenes)
            for scene in scenes:
                scene["duration_seconds"] = scene.get("duration_seconds", 120) + per_scene


def _assign_chapter_numbers(story_data: dict, num_chapters: int, chapter_duration: int) -> None:
    """Asegura que todas las escenas tengan chapter_number asignado."""
    scenes = story_data.get("scenes", [])
    if num_chapters <= 1:
        for scene in scenes:
            scene["chapter_number"] = 1
        return

    # Si las escenas ya tienen chapter_number, respetar
    has_chapters = any(s.get("chapter_number") for s in scenes)
    if has_chapters:
        return

    # Distribuir escenas en capítulos por duración
    target_per_chapter = chapter_duration * 60
    current_ch = 1
    current_duration = 0
    for scene in scenes:
        scene["chapter_number"] = current_ch
        current_duration += scene.get("duration_seconds", 120)
        if current_duration >= target_per_chapter and current_ch < num_chapters:
            current_ch += 1
            current_duration = 0