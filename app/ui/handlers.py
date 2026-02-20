import json

import httpx
from loguru import logger

from app.core.models_config import DEFAULT_MODEL, MODEL_MAP

API_BASE = "http://localhost:8000/api/v1"


def _stars(score: int | None) -> str:
    if not score:
        return ""
    return "★" * score + "☆" * (5 - score)


def run_analysis(dream_text: str, model_label: str):
    empty = ("", "", "", "", "", "", "", "", "", [])

    if not dream_text or len(dream_text.strip()) < 10:
        yield ("❌ Please enter a longer dream (at least 10 characters)", *empty)
        return

    model = MODEL_MAP.get(model_label, DEFAULT_MODEL)
    model_name = model_label.split("(")[0].strip()

    # Phase 1: create dream
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{API_BASE}/dreams", json={"content": dream_text})
            resp.raise_for_status()
            dream_id = resp.json()["id"]
    except Exception as e:
        yield (f"❌ Failed to create dream: {e}", *empty)
        return

    def out(status, gen="", ss="", s="", es="", e="", ts="", t="", sy="", similar=None):
        return (status, gen, ss, s, es, e, ts, t, sy, similar or [])

    # Phase 2: stream generalist
    generalist_text = ""
    yield out(f"⏳ Generalist analyzing with {model_name}...")

    try:
        with httpx.Client(timeout=120) as client:
            with client.stream(
                "POST",
                f"{API_BASE}/dreams/{dream_id}/stream-generalist",
                params={"model": model},
            ) as response:
                response.raise_for_status()
                for chunk in response.iter_text():
                    generalist_text += chunk
                    yield out("⏳ Generalist analyzing...", generalist_text)
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield out(f"❌ Generalist error: {e}", generalist_text)
        return

    # Phase 3: stream specialists + rating + synthesizer via SSE
    symbol_text = ""
    emotion_text = ""
    theme_text = ""
    synthesis_text = ""
    scores: dict = {}

    yield out("⏳ Running specialists...", generalist_text)

    try:
        with httpx.Client(timeout=300) as client:
            with client.stream(
                "POST",
                f"{API_BASE}/dreams/{dream_id}/stream-analyze",
                params={"model": model},
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = json.loads(line[6:])

                    if data.get("event") == "scores":
                        scores = data["data"]
                    elif data.get("event") == "done":
                        break
                    elif "token" in data:
                        agent = data["agent"]
                        token = data["token"]
                        if agent == "symbol_specialist":
                            symbol_text += token
                        elif agent == "emotion_specialist":
                            emotion_text += token
                        elif agent == "theme_specialist":
                            theme_text += token
                        elif agent == "synthesizer":
                            synthesis_text += token

                    yield out(
                        "⏳ Analyzing...",
                        generalist_text,
                        _stars(scores.get("symbol")),
                        symbol_text,
                        _stars(scores.get("emotion")),
                        emotion_text,
                        _stars(scores.get("theme")),
                        theme_text,
                        synthesis_text,
                    )
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        yield out(
            f"❌ Pipeline error: {e}",
            generalist_text,
            _stars(scores.get("symbol")),
            symbol_text,
            _stars(scores.get("emotion")),
            emotion_text,
            _stars(scores.get("theme")),
            theme_text,
            synthesis_text,
        )
        return

    # Fetch similar dreams
    similar_dreams = []
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{API_BASE}/dreams/{dream_id}/similar?limit=3")
            resp.raise_for_status()
            data = resp.json()
            # Format for Gradio Dataframe: list of lists
            similar_dreams = [[d["id"], d["content"], d["similarity"]] for d in data]
    except Exception as e:
        logger.error(f"Similar dreams error: {e}")

    yield out(
        "✅ Complete",
        generalist_text,
        _stars(scores.get("symbol")),
        symbol_text,
        _stars(scores.get("emotion")),
        emotion_text,
        _stars(scores.get("theme")),
        theme_text,
        synthesis_text,
        similar_dreams,
    )


def get_past_dreams():
    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(f"{API_BASE}/dreams?limit=50")
            response.raise_for_status()
            dreams = response.json()
    except Exception as e:
        logger.error(f"UI error fetching dreams: {e}")
        return [[f"Error: {e}", "", "", "", ""]]

    if not dreams:
        return [["No dreams yet", "", "", "", ""]]

    rows = []
    for dream in dreams:
        analyses = dream.get("analyses", [])
        first = analyses[0] if analyses else None
        rows.append(
            [
                str(dream["id"]),
                dream["created_at"][:16].replace("T", " "),
                dream["content"][:80] + ("..." if len(dream["content"]) > 80 else ""),
                first["model_used"] if first else "",
                first["content"][:100] + "..." if first else "",
            ]
        )

    return rows
