"""
Flow:
    generalist → specialists (parallel) → rating → synthesizer

If generalist_output is pre-seeded (from streaming endpoint), generalist node is skipped.
"""

from langgraph.graph import END, START, StateGraph

from app.workflows.nodes import (
    generalist_node,
    rating_node,
    specialists_node,
    synthesizer_node,
)
from app.workflows.state import DreamAnalysisState


def _route_start(state: DreamAnalysisState) -> str:
    """Skip generalist if output already provided (e.g. from streaming endpoint)."""
    return "specialists" if state["generalist"] else "generalist"


def _build_graph():
    graph = StateGraph(DreamAnalysisState)

    graph.add_node("generalist", generalist_node)
    graph.add_node("specialists", specialists_node)
    graph.add_node("rating", rating_node)
    graph.add_node("synthesizer", synthesizer_node)

    graph.add_conditional_edges(START, _route_start, {
        "generalist": "generalist",
        "specialists": "specialists",
    })
    graph.add_edge("generalist", "specialists")
    graph.add_edge("specialists", "rating")
    graph.add_edge("rating", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()


dream_graph = _build_graph()


async def run_dream_analysis(
    dream_id: int,
    dream: str,
    model: str,
    generalist_output: str = "",
) -> DreamAnalysisState:
    """Run the pipeline. Pass generalist_output to skip the generalist node."""
    initial: DreamAnalysisState = {
        "dream_id": dream_id,
        "dream": dream,
        "model": model,
        "generalist": generalist_output,
        "symbol": "",
        "emotion": "",
        "theme": "",
        "synthesis": "",
        "symbol_analysis_id": 0,
        "emotion_analysis_id": 0,
        "theme_analysis_id": 0,
        "scores": {},
        "retried": [],
    }

    result: DreamAnalysisState = await dream_graph.ainvoke(initial)  # type: ignore[assignment]
    return result
