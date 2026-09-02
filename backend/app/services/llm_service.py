"""Servicio de LLM local via llama-cpp-python."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backend.config import settings

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

_llm_instance = None


def get_llm():
    """Singleton perezoso del LLM. Se carga/descarga para gestionar VRAM."""
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    try:
        from llama_cpp import Llama
    except ImportError:
        logger.error("llama-cpp-python no esta instalado.")
        raise

    logger.info("Cargando LLM en VRAM: %s", settings.llm_model_path)
    _llm_instance = Llama(
        model_path=str(settings.llm_model_path),
        n_gpu_layers=settings.llm_n_gpu_layers,
        n_ctx=settings.llm_context_size,
        temperature=settings.llm_temperature,
        verbose=False,
    )
    logger.info("LLM cargado correctamente.")
    return _llm_instance


def unload_llm() -> None:
    """Descarga el LLM de VRAM."""
    global _llm_instance
    if _llm_instance is not None:
        del _llm_instance
        _llm_instance = None
        logger.info("LLM descargado de VRAM.")


def is_llm_available() -> bool:
    """Verifica si el LLM local esta disponible."""
    if not settings.llm_model_path.exists():
        return False
    try:
        from llama_cpp import Llama
        return True
    except Exception as exc:
        # llama-cpp puede estar instalado pero no poder cargar llama.dll/CUDA.
        # En ese caso se debe usar el generador de respaldo, no abortar el
        # pipeline antes de crear las escenas.
        logger.warning("LLM local no disponible (%s).", exc)
        return False


# ──────────────────────────────────────────────────────────
# NARRACIONES DE ANIME REALISTAS PARA EL MOCK
# ──────────────────────────────────────────────────────────

_ANIME_NARRATIONS = [
    """La ciudad de Nexus Prime nunca dormía. Sus luces de neón parpadeaban como estrellas caídas sobre el asfalto mojado, y entre las sombras que proyectaban los rascacielos, las historias de sus habitantes se entretejían en un tapiz invisible de destinos cruzados.

Akira lo sabía mejor que nadie. Había crecido en esas callejuelas, había aprendido a leer el lenguaje silencioso de la ciudad: el ritmo de los pasos que se aceleran cuando alguien teme algo, la forma en que las luces parpadean antes de que ocurra algo importante.

—No deberías estar aquí —dijo una voz detrás de él.

No se giró de inmediato. Primero escuchó: el eco de esa voz, la forma en que el aire cambió con su presencia. Luego, lentamente, se volvió para enfrentar a quien se había atrevido a seguirlo hasta este rincón perdido del mundo.

Era Yuki. Claro que era Yuki.

—Nunca aprenderás a quedarte donde es seguro —respondió Akira, pero sin el filo que pretendía. Había algo en la forma en que ella lo miraba que siempre desarmaba sus defensas más cuidadosamente construidas.

—Y tú nunca aprenderás que no puedes cargar con el mundo entero solo —replicó ella, acercándose con esa calma que él tanto envidiaba y jamás admitiría.

El silencio que siguió habló más que cualquier palabra. Entre ellos flotaban meses de momentos no dichos, de miradas que duraron un segundo demasiado, de manos que casi se rozaron y se retiraron a tiempo.

—El Consejo se ha movido —dijo finalmente Akira, volviendo a lo que importaba, a lo que siempre había sido más fácil que enfrentar lo que sentía—. Tienen el Artefacto. Si no actuamos antes del amanecer...

—Lo sé —interrumpió Yuki—. Por eso estoy aquí.

Y en esas cuatro palabras simples, Akira encontró algo que no había buscado pero que desperadamente necesitaba: no estaba solo. Nunca lo había estado.""",

    """El entrenamiento había comenzado antes del amanecer, como siempre. Pero esta vez, algo era diferente.

Kaito sintió el cambio antes de verlo: una vibración en el suelo, casi imperceptible, que le subió por las plantas de los pies hasta el corazón. Cuando el maestro Ryu apareció al fondo del patio de entrenamiento, supo que las cosas nunca volverían a ser como antes.

—Hoy —dijo el maestro Ryu, con esa voz que cortaba el aire como acero— aprenderás la verdad sobre tu linaje.

Kaito aguantó la respiración. Llevaba años esperando este momento y ahora que había llegado, descubrió que el miedo era mucho mayor que la curiosidad.

—Mi linaje —repitió, como si las palabras pudieran volverse más reales si las decía en voz alta—. ¿Qué tiene de especial mi linaje?

El maestro Ryu sacó algo de entre los pliegues de su ropa: un cristal negro, del tamaño de un puño, que absorbía la luz en lugar de reflejarla. Lo colocó en el centro del patio y dio tres pasos hacia atrás.

—Tócalo —ordenó.

—¿Por qué? ¿Qué...?

—Tócalo.

Kaito avanzó con pasos medidos. El cristal pulsaba con un ritmo que no debería ser posible en ningún objeto inerte. Cuando extendió la mano y sus dedos rozaron la superficie fría, el mundo explotó en luz blanca.

Y en esa luz, vio todo: el pasado que le habían ocultado, el futuro que lo esperaba, el peso terrible de lo que significaba ser quien era.

Cuando la visión terminó, estaba de rodillas en el suelo. El maestro Ryu lo observaba con una expresión que Kaito tardó un momento en reconocer.

Era orgullo. Y algo más. Algo parecido al miedo.""",

    """Tres días habían pasado desde la traición. Tres días que se habían sentido como tres años.

Seraphina caminaba por los pasillos del Palacio de Cristal con la espalda erguida y el rostro inexpresivo, porque le habían enseñado desde pequeña que las princesas no mostraban dolor. Las princesas sonreían. Las princesas saludaban. Las princesas fingían que todo estaba perfectamente bien mientras el mundo se desmoronaba a sus pies.

El Duque Valen la esperaba en la sala del consejo. Se puso de pie cuando ella entró, un gesto de respeto protocolario que a ella le resultó absolutamente insoportable viniendo de él.

—Alteza —dijo con esa voz suave que había aprendido a odiar—. Gracias por recibirme.

—No tenía opción —respondió Seraphina, tomando su lugar en la cabecera de la mesa—. El protocolo lo exige.

Una sonrisa apenas perceptible cruzó el rostro del Duque. Era el tipo de sonrisa que decía: ambos sabemos que este protocolo también fue tu idea.

—Hay asuntos que discutir —comenzó él.

—Hay mentiras que deshacer —lo interrumpió ella, y vio con satisfacción cómo la máscara de él se agrietaba apenas—. Sé lo que hiciste, Valen. Sé por qué lo hiciste. Y lo que necesitas entender es que no importa.

—¿No importa? —repitió él, y esta vez había algo real en su voz, algo que no era el personaje cuidadosamente construido sino la persona debajo—. Seraphina, lo hice para protegerte.

—No —dijo ella con una calma que le había costado tres días construir—. Lo hiciste para protegerte a ti mismo. Y lo que te sale cuando mentirte ya no es suficiente.

El silencio que siguió fue el más honesto que habían compartido en años.""",

    """El bosque de cristal nunca había sido un lugar seguro, pero esta noche era especialmente hostil.

Los árboles de cuarzo translúcido captaban la luz de la luna y la descomponían en espectros que bailaban entre las ramas, creando sombras que no correspondían a ninguna forma real. Era hermoso. Era aterrador. Era, pensó Lyra mientras avanzaba entre los troncos luminosos, exactamente el tipo de lugar donde las cosas importantes siempre terminaban por suceder.

Su mano derecha apretaba el cristal de memoria que había encontrado en las ruinas. Pulsaba con un calor suave, rítmico, casi como un corazón.

—Sé que estás ahí —dijo en voz alta.

El silencio respondió. Pero no era el silencio vacío del bosque desierto; era el silencio lleno de alguien que contiene la respiración.

—No tengo paciencia para los juegos esta noche —continuó Lyra, deteniéndose en un pequeño claro donde la luz se concentraba en un charco de plata líquida—. Han muerto personas. Gente que yo conocía. Y tú sabes por qué.

Una figura emergió de entre los árboles. Era más joven de lo que Lyra había esperado, con esa apariencia de no haber dormido en días que ella reconocía porque se la había visto en el espejo todas las mañanas de la última semana.

—No lo sé todo —dijo la figura—. Solo sé lo suficiente como para tener miedo.

—Entonces empezamos en el mismo punto —respondió Lyra—. Cuéntame desde el principio. Y por favor, esta vez sin omisiones estratégicas.""",

    """El momento de la verdad siempre llegaba de formas inesperadas.

Para Dorian, llegó en forma de una carta sellada con cera negra que encontró bajo la puerta de su apartamento. Sin remitente. Sin dirección de retorno. Solo su nombre escrito con una caligrafía que reconoció inmediatamente porque era la suya propia, de cinco años atrás.

Eso era imposible.

O debería serlo.

Abrió la carta con manos que se negaban a temblar, aunque todo lo demás en su cuerpo sí lo hacía. El papel era el mismo que usaba entonces, con el mismo leve olor a madera de cedro que tenía su escritorio universitario. Y el mensaje era tan simple que su sencillez misma era escalofriante:

«No confíes en quien te lo ofrezca. El precio es más alto de lo que imaginas.»

Dorian leyó las palabras tres veces. Luego las leyó una vez más, buscando algo que se le hubiera escapado. No encontró nada, y eso era el problema: el mensaje era perfectamente claro. Alguien, desde el pasado, le estaba advirtiendo sobre el futuro.

Lo cual significaba que alguien había tenido acceso a su futuro.

Lo cual significaba que lo que el Consejo le había ofrecido la noche anterior era exactamente lo que la carta mencionaba.

—¿Cuánto tiempo llevas ahí? —preguntó sin girarse, porque había sentido la presencia antes de escuchar los pasos.

—El suficiente —respondió la voz de Aria desde la puerta—. Suficiente para saber que vas a necesitar ayuda con lo que sea que acabas de descubrir.

Dorian finalmente se giró. La mirò durante un largo momento, evaluando, calculando, y luego, porque no tenía realmente otra opción, tomó una decisión que cambiaría el curso de todo.

—Cierra la puerta —dijo—. Y escucha.""",

    """La batalla había terminado. La victoria tenía el sabor amargo de todo aquello a lo que habían renunciado para alcanzarla.

Aria se arrodilló junto al cuerpo caído, sin importarle el barro ni la lluvia que empapaba su ropa. Alrededor de ella, el campo de batalla era un paisaje de silencio y destrucción: lo que había sido un lugar de poder reducido a escombros, lo que había sido un ejército convertido en historia.

—Deberías levantarte —dijo una voz a su lado. Kaito. Siempre Kaito.

—Dame un momento —respondió ella, sin apartar los ojos del rostro de quien yacía ante ella. Era extraño verlo así: sin la arrogancia, sin la certeza que había sido su armadura durante años. En la derrota, todos los rostros se igualaban.

—¿Lo lloras? —preguntó Kaito, y en su voz no había juicio, solo curiosidad genuina.

—Lloro lo que podría haber sido —dijo Aria—. Lloro la versión de esta historia donde las cosas salían de otra manera. Donde las decisiones eran diferentes. Donde nadie tenía que llegar hasta aquí.

Kaito se quedó en silencio durante un momento. Luego se sentó en el barro a su lado, sin importarle tampoco su ropa, sin importarle el protocolo ni las jerarquías ni ninguna de las cosas que normalmente importaban.

—El Consejo querrá saber cómo reportar esto —dijo finalmente.

—El Consejo puede esperar.

—La ciudad entera está esperando noticias.

—La ciudad puede esperar también.

Y así, en el silencio mojado de ese campo que había sido una guerra y ahora era solo un lugar triste, dos personas que habían atravesado lo imposible se permitieron, por primera vez en mucho tiempo, simplemente estar."""
]

_ANIME_TITLES = [
    "Crónicas del Destino Fragmentado",
    "El Último Guerrero del Nexo",
    "Lazos que el Tiempo No Borra",
    "La Sombra del Clan Eterno",
    "Renacimiento en las Cenizas",
    "El Pacto de los Elegidos",
    "Corazón de Cristal Roto",
    "Más Allá del Horizonte Prohibido",
]

_ANIME_SYNOPSES = [
    "En un mundo donde la magia y la tecnología coexisten en una tensión frágil, un joven guerrero descubre que su linaje lo convierte en la pieza central de un conflicto que lleva siglos gestándose en las sombras. Junto a una aliada inesperada y un mentor cuya lealtad nunca fue lo que parecía, deberá navegar entre traiciones y verdades ocultas mientras lucha por proteger todo lo que ama. Pero el precio de la victoria podría ser exactamente lo que más teme perder.",
    "Cuando la princesa heredera de un imperio en decadencia descubre que el consejero en quien más confía ha manipulado los hilos de su reino durante décadas, debe tomar una decisión que cambiará el curso de la historia. Con la ayuda de un grupo de rebeldes cuyas motivaciones no son tan claras como parecen, emprende una misión que la obligará a cuestionar todo lo que creía saber sobre el honor, la lealtad y el verdadero significado del poder.",
    "Cinco estudiantes de la Academia Elite de Nexus Prime reciben poderes que no pidieron en la peor semana de sus vidas. Lo que parece una bendición resulta ser la señal de que una antigua profecía está a punto de cumplirse, y que ellos son los únicos que pueden detener lo que se avecina. El problema: no confían los unos en los otros, y la entidad que despertó sus poderes tiene sus propias razones para haberlos elegido.",
]


def generate_mock(prompt: str, system_prompt: str) -> str:
    """Genera respuestas JSON simulando la IA con historias de anime realistas."""
    import json
    import re

    # ── 1. Guionista (Writer) ──────────────────────────────
    if ("scenes" in system_prompt and "characters" in system_prompt) or \
       ("escenas" in system_prompt.lower() and "personajes" in system_prompt.lower()):

        # Extraer parámetros
        duration = 22
        num_chars = 3
        genres = ["aventura", "accion"]
        style = "anime"
        num_chapters = 1
        chapter_duration = 20

        dur_match = re.search(r"[Dd]uracion.*?(\d+)\s*minutos", prompt)
        if dur_match:
            duration = int(dur_match.group(1))

        chars_match = re.search(r"[Nn]umero de personajes.*?(\d+)", prompt)
        if chars_match:
            num_chars = int(chars_match.group(1))

        genres_match = re.search(r"[Gg]eneros?:?\s*(.*?)[\n\-]", prompt)
        if genres_match:
            genres = [g.strip() for g in genres_match.group(1).split(",") if g.strip()]

        style_match = re.search(r"[Ee]stilo.*?:\s*(\w+)", prompt)
        if style_match:
            style = style_match.group(1).strip()

        chapters_match = re.search(r"[Nn]umero de capitulos.*?(\d+)", prompt)
        if chapters_match:
            num_chapters = int(chapters_match.group(1))
        elif duration > 25:
            num_chapters = max(2, duration // chapter_duration)

        ch_dur_match = re.search(r"[Dd]uracion por capitulo.*?(\d+)", prompt)
        if ch_dur_match:
            chapter_duration = int(ch_dur_match.group(1))

        # Calcular escenas necesarias
        total_seconds_needed = duration * 60
        seconds_per_scene = 240  # 4 minutos por escena
        num_scenes = max(6, total_seconds_needed // seconds_per_scene)

        # Personajes
        char_data = [
            {"name": "Akira Ryū", "role": "Protagonista",
             "description": "Joven de 18 años con un pasado doloroso que oculta bajo una fachada de indiferencia. Perdió a su familia en el Gran Colapso y desde entonces lucha para encontrar su propósito. Su mayor fortaleza es su intuición; su mayor debilidad, su incapacidad para pedir ayuda.",
             "appearance": f"{style} style, joven de 18 años, cabello negro despeinado con mechones que caen sobre los ojos, ojos azul oscuro profundo, cicatriz diagonal en la mejilla izquierda, complexión atlética, viste chaqueta de cuero roja desgastada sobre camiseta negra, pantalón cargo gris, botas militares",
             "voice_type": "Masculina ronca"},
            {"name": "Yuki Shirogane", "role": "Secundario",
             "description": "La única persona que genuinamente comprende a Akira, aunque él se resista a admitirlo. Analítica y empática a partes iguales, tiene la capacidad de ver lo mejor en las personas incluso cuando estas no lo ven en sí mismas. Esconde una melancolía profunda detrás de su calma aparente.",
             "appearance": f"{style} style, chica de 17 años, cabello plateado largo hasta la cintura con reflejos azulados, ojos violeta iridiscentes, piel clara, complexión esbelta, viste uniforme modificado de la Academia con detalles dorados en los bordes, siempre lleva un cristal de memoria en el cuello",
             "voice_type": "Femenina suave"},
            {"name": "Valen Oscuro", "role": "Antagonista",
             "description": "Un hombre que una vez fue héroe y eligió convertirse en villano porque el mundo lo decepcionó. Su crueldad es calculada, nunca impulsiva. Cree genuinamente que lo que hace es necesario, y esa convicción lo hace más peligroso que cualquier monstruo que actúe por puro mal.",
             "appearance": f"{style} style, hombre de 35 años, cabello negro con canas en las sienes, ojos grises como acero, mandíbula cuadrada, cicatriz vertical que atraviesa el ojo izquierdo, viste abrigo largo negro con hombreras plateadas, guantes de cuero",
             "voice_type": "Masculina profunda"},
            {"name": "Lyra Estrellada", "role": "Interes Romantico",
             "description": "Miembro de la resistencia con un secreto que podría cambiar el equilibrio de poder entre facciones. Independiente hasta el punto de la autodestrucción, aprende lentamente que la fortaleza no está en no necesitar a nadie sino en elegir a quién necesitar.",
             "appearance": f"{style} style, chica de 19 años, cabello castaño rojizo ondulado hasta los hombros, ojos verdes con manchas doradas, pecas en la nariz y mejillas, complexión musculosa y ágil, viste ropa táctica oscura con emblema de la resistencia bordado en el brazo",
             "voice_type": "Femenina aguda"},
            {"name": "Maestro Ryu", "role": "Mentor",
             "description": "El guía cuya lealtad nunca fue exactamente lo que Akira creía. Guardador de verdades que ha callado durante décadas por razones que, cuando finalmente se revelan, son simultáneamente comprensibles e imperdonables.",
             "appearance": f"{style} style, hombre de 60 años, cabello blanco trenzado, ojos negros profundos que parecen ver demasiado, arrugas de expresión marcadas, complexión delgada pero con una presencia que llena el espacio, viste ropa tradicional gris con símbolos del antiguo orden",
             "voice_type": "Masculina profunda"},
            {"name": "Seraphina", "role": "Rival",
             "description": "La rival que se convierte en aliada, aunque ninguno de los dos lo admitiría. Compite con Akira por motivaciones que gradualmente revelan ser más similares a las suyas de lo que cualquiera de los dos quisiera reconocer.",
             "appearance": f"{style} style, chica de 18 años, cabello rojo vivo cortado asimétricamente, ojos dorados con pupila vertical, complexión atlética y grácil, viste armadura ligera color carmesí con detalles negros, siempre lleva dos dagas enfundadas en los muslos",
             "voice_type": "Femenina aguda"},
        ]
        characters = char_data[:num_chars]
        char_names = [c["name"] for c in characters]

        # Títulos de capítulos
        chapter_titles_pool = [
            "El Despertar del Elegido",
            "Sombras del Pasado",
            "La Traición Revelada",
            "El Precio de la Verdad",
            "En el Ojo de la Tormenta",
            "Alianzas Imposibles",
            "El Momento Decisivo",
            "Más Allá del Punto de No Retorno",
        ]

        # Construir capítulos
        chapters_meta = []
        for ch in range(1, num_chapters + 1):
            chapters_meta.append({
                "chapter_number": ch,
                "title": chapter_titles_pool[(ch - 1) % len(chapter_titles_pool)],
                "synopsis": f"En este capítulo, los eventos escalan y {char_names[0]} debe enfrentar consecuencias inesperadas de sus decisiones anteriores.",
                "cliffhanger": f"Cuando todo parecía decidido, una revelación cambia las reglas del juego..." if ch < num_chapters else None
            })

        # Construir escenas
        scenes = []
        emotions = ["intriga", "drama", "tension", "accion", "giro", "melancolia", "impacto", "esperanza", "tragedia", "resolucion"]
        cameras = ["close-up", "plano general", "travelling", "plano medio", "zoom dramatico", "contrapicado", "plano aereo"]

        scenes_per_chapter = max(3, num_scenes // max(1, num_chapters))
        global_scene = 1

        for ch_num in range(1, num_chapters + 1):
            for sc_idx in range(scenes_per_chapter):
                narr_idx = (global_scene - 1) % len(_ANIME_NARRATIONS)
                emotion_idx = ((ch_num - 1) * scenes_per_chapter + sc_idx) % len(emotions)
                cam_idx = ((ch_num - 1) * scenes_per_chapter + sc_idx) % len(cameras)

                scenes.append({
                    "scene_number": global_scene,
                    "chapter_number": ch_num,
                    "title": f"Cap.{ch_num} — {['El encuentro', 'La revelación', 'La decisión', 'El conflicto', 'La resolución'][sc_idx % 5]}",
                    "narration": _ANIME_NARRATIONS[narr_idx],
                    "emotion": emotions[emotion_idx],
                    "camera": cameras[cam_idx],
                    "character_names": char_names[:2],
                    "duration_seconds": seconds_per_scene,
                })
                global_scene += 1

        # Ajustar para alcanzar duración mínima
        current_total = len(scenes) * seconds_per_scene
        if current_total < total_seconds_needed:
            extra_needed = total_seconds_needed - current_total
            extra_scenes = max(1, extra_needed // seconds_per_scene)
            for ex in range(int(extra_scenes)):
                ch_for_extra = num_chapters  # Añadir al último capítulo
                scenes.append({
                    "scene_number": global_scene,
                    "chapter_number": ch_for_extra,
                    "title": f"Epílogo — Parte {ex + 1}",
                    "narration": _ANIME_NARRATIONS[(global_scene - 1) % len(_ANIME_NARRATIONS)],
                    "emotion": "resolucion",
                    "camera": "plano general",
                    "character_names": char_names[:1],
                    "duration_seconds": seconds_per_scene,
                })
                global_scene += 1

        title_idx = hash(str(genres)) % len(_ANIME_TITLES)
        synopsis_idx = hash(str(genres + [style])) % len(_ANIME_SYNOPSES)

        story = {
            "title": _ANIME_TITLES[title_idx],
            "synopsis": _ANIME_SYNOPSES[synopsis_idx],
            "world_building": f"Un universo de {style} donde la tecnología arcana y la magia ancestral coexisten en equilibrio frágil. Las ciudades flotan sobre nubes de energía, y los clanes guerreros controlan los nodos de poder que mantienen el mundo en pie.",
            "chapters": chapters_meta,
            "characters": characters,
            "scenes": scenes,
        }
        return json.dumps(story, ensure_ascii=False)

    # ── 2. Editor ─────────────────────────────────────────
    if "editor" in system_prompt.lower() or "score" in prompt.lower() or "revisa" in prompt.lower():
        return json.dumps({
            "score": 92,
            "issues": [],
            "fixes_applied": [
                "Ritmo narrativo optimizado para mantener tensión sostenida",
                "Coherencia de personajes verificada en todas las escenas",
                "Transiciones entre capítulos mejoradas",
            ]
        }, ensure_ascii=False)

    # ── 3. Storyboard ─────────────────────────────────────
    if ("prompts detallados" in system_prompt.lower()
            or "image prompt" in prompt.lower()
            or "estilo:" in prompt.lower()
            or "generas prompts" in system_prompt.lower()):

        emo = "dramatic"
        if "Emocion:" in prompt:
            emo = prompt.split("Emocion:")[1].split("\n")[0].strip()
        cam = "wide shot"
        if "Camara:" in prompt:
            cam = prompt.split("Camara:")[1].split("\n")[0].strip()
        style = "anime"
        if "Estilo:" in prompt:
            style = prompt.split("Estilo:")[1].split("\n")[0].strip()
        chars = ""
        if "Personajes en escena:" in prompt:
            chars = prompt.split("Personajes en escena:")[1].split("\n")[0].strip()

        char_part = f", {chars[:100]}" if chars else ""
        return (
            f"{style} style, ultra-detailed, cinematic lighting, {emo} atmosphere, "
            f"{cam} composition{char_part}, "
            f"masterwork quality, vibrant colors, dramatic shadows, "
            f"high contrast, professional anime art direction, "
            f"volumetric lighting, detailed background, "
            f"emotional depth, award-winning illustration"
        )

    # ── 4. SEO ────────────────────────────────────────────
    if "seo" in system_prompt.lower() or "seo" in prompt.lower() or "hashtag" in prompt.lower():
        title = "Crónicas del Destino"
        if "Titulo:" in prompt:
            title = prompt.split("Titulo:")[1].split("\n")[0].strip()
        synopsis = ""
        if "Sinopsis:" in prompt:
            synopsis = prompt.split("Sinopsis:")[1].split("\n")[0].strip()[:100]

        return json.dumps({
            "youtube": {
                "title": f"{title} | Historia Narrada de Anime [{_random_year()}]",
                "description": f"🎌 {synopsis}\n\n📖 Una historia épica narrada con calidad cinematográfica.\n\n⏰ CAPÍTULOS:\n0:00 — Introducción\n5:00 — El Conflicto Principal\n15:00 — El Giro Inesperado\n25:00 — La Resolución Épica\n\n🔔 Suscríbete para más historias narradas de anime\n#anime #historianarrada #animereaction",
                "tags": ["historia narrada", "anime", "storytime", "narracion", "anime español", "drama anime", "historia anime", "narrador", "storytime anime"]
            },
            "tiktok": {
                "title": f"Este final te dejará sin palabras 😱 | {title[:40]}",
                "description": f"No podrás parar de escuchar esta historia 🎌 {synopsis[:80]}... #anime #historianarrada #fyp",
                "tags": ["#anime", "#historianarrada", "#fyp", "#storytime", "#animeesp", "#viral", "#drama"]
            },
            "facebook": {
                "title": f"Historia Completa: {title}",
                "description": f"Una historia épica de anime narrada completa. {synopsis} Perfecta para escuchar mientras trabajas o te relajas.",
                "tags": ["anime", "historia narrada", "drama", "storytime"]
            },
            "shorts": {
                "title": f"El momento más épico de {title[:35]}... 🔥",
                "description": f"El giro que nadie esperaba #anime #shorts #historianarrada #viral",
                "tags": ["#shorts", "#anime", "#viral", "#historianarrada"]
            },
            "thumbnail_text": title[:25].upper()
        }, ensure_ascii=False)

    return json.dumps({"response": "Respuesta generada correctamente."}, ensure_ascii=False)


def _random_year() -> str:
    import datetime
    return str(datetime.datetime.now().year)


def generate(prompt: str, system_prompt: str = "", max_tokens: int = 8192) -> str:
    """Genera texto real con el modelo local configurado.

    Una respuesta simulada no es una salida de producción: si el modelo no se
    puede ejecutar, la generación se detiene y deja un error diagnósticable.
    """
    if not is_llm_available():
        raise RuntimeError(
            "El modelo de guion local no está disponible. Revisa models/llm y logs/backend.log."
        )

    try:
        llm = get_llm()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=settings.llm_temperature,
        )
        content = response["choices"][0]["message"]["content"]
        return content.strip()
    except Exception as exc:
        logger.exception("LLM local falló: %s", exc)
        unload_llm()
        raise RuntimeError(
            "El modelo de guion local no pudo generar contenido. Revisa logs/backend.log."
        ) from exc
