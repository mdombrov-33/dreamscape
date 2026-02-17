from typing import TypedDict


class DreamAnalysisState(TypedDict):
    dream_id: int
    dream: str
    model: str
    # Agent outputs
    generalist: str
    symbol: str
    emotion: str
    theme: str
    synthesis: str
    # DB row IDs - needed to write scores back after rating
    symbol_analysis_id: int
    emotion_analysis_id: int
    theme_analysis_id: int
    # Scores from rating node (avg of depth + relevance + insight)
    scores: dict[str, int]
    # Specialists already retried - prevents infinite retry loops
    retried: list[str]
