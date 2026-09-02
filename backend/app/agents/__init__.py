"""Agentes de generación de historias.
La importación del grafo se hace de forma lazy para evitar imports circulares.
"""

__all__ = ["build_story_graph"]


def build_story_graph():
    """Importa y construye el grafo de forma lazy."""
    from backend.app.agents.graph import build_story_graph as _build
    return _build()