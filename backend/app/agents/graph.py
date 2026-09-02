"""Grafo LangGraph que orquesta todos los agentes."""
from __future__ import annotations

import logging
from typing import Any, AsyncGenerator

from langgraph.graph import StateGraph, END

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

logger = logging.getLogger(__name__)


# Estado compartido del grafo
class StoryState(dict):
    """Estado mutable que fluye entre agentes."""
    pass


def build_story_graph():
    """Construye y devuelve el grafo de produccion con soporte de capítulos."""
    graph = StateGraph(StoryState)

    # Nodos (un agente cada uno)
    graph.add_node("writer", run_writer)
    graph.add_node("chapter_splitter", run_chapter_splitter)
    graph.add_node("editor", run_editor)
    graph.add_node("storyboard", run_storyboard)
    graph.add_node("character_designer", run_character_designer)
    graph.add_node("visual_director", run_visual_director)
    graph.add_node("image_generator", run_image_generator)
    graph.add_node("voice_generator", run_voice_generator)
    graph.add_node("seo_generator", run_seo_generator)
    graph.add_node("qa", run_qa)

    # Flujo secuencial con divisor de capítulos tras el escritor
    graph.set_entry_point("writer")
    graph.add_edge("writer", "chapter_splitter")
    graph.add_edge("chapter_splitter", "editor")
    graph.add_edge("editor", "storyboard")
    graph.add_edge("storyboard", "character_designer")
    graph.add_edge("character_designer", "visual_director")
    graph.add_edge("visual_director", "image_generator")
    graph.add_edge("image_generator", "voice_generator")
    graph.add_edge("voice_generator", "seo_generator")
    graph.add_edge("seo_generator", "qa")
    graph.add_edge("qa", END)

    return graph.compile()