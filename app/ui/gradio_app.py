import json

import gradio as gr
import httpx
import numpy as np
from loguru import logger

from app.core.models_config import DEFAULT_MODEL, DEFAULT_MODEL_LABEL, MODEL_LABELS, MODEL_MAP

API_BASE = "http://localhost:8000/api/v1"

_whisper = None


def _get_whisper():
    global _whisper
    if _whisper is None:
        from transformers import pipeline

        logger.info("Loading Whisper model...")
        _whisper = pipeline(
            "automatic-speech-recognition", model="openai/whisper-small", device="cpu"
        )  # noqa: E501
        logger.info("Whisper loaded.")
    return _whisper


def transcribe_audio(audio):
    if audio is None:
        return ""
    sample_rate, data = audio
    if data.ndim > 1:
        data = data.mean(axis=1)
    audio_float = data.astype(np.float32) / 32768.0
    result: dict = _get_whisper()({"sampling_rate": sample_rate, "raw": audio_float})  # type: ignore[assignment]
    return result["text"].strip()


def _stars(score: int | None) -> str:
    if not score:
        return ""
    return "★" * score + "☆" * (5 - score)


def run_analysis(dream_text: str, model_label: str):
    empty = ("", "", "", "", "", "", "", "", "")

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

    def out(status, gen="", ss="", s="", es="", e="", ts="", t="", sy=""):
        return (status, gen, ss, s, es, e, ts, t, sy)

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


with gr.Blocks(theme="soft", title="Dreamscape") as gradio_ui:
    gr.Markdown("# 🌙 Dreamscape\n### Multi-Agent Dream Analysis")

    with gr.Tabs():
        with gr.Tab("✨ New Dream"):
            model_dropdown = gr.Dropdown(
                label="Model",
                choices=MODEL_LABELS,
                value=DEFAULT_MODEL_LABEL,
            )

            with gr.Row():
                mic_input = gr.Audio(
                    sources=["microphone"], type="numpy", label="🎙️ Record your dream"
                )
                transcribe_btn = gr.Button("📝 Transcribe", size="sm", scale=0)

            dream_input = gr.Textbox(
                label="Dream",
                placeholder="I was flying through a dark forest, when suddenly...",
                lines=6,
                max_lines=20,
            )

            transcribe_btn.click(fn=transcribe_audio, inputs=[mic_input], outputs=[dream_input])

            analyze_btn = gr.Button("🔮 Analyze Dream", variant="primary", size="lg")

            status_output = gr.Textbox(label="", lines=1, max_lines=1, show_label=False)

            gr.Markdown(
                "**Pipeline:** Generalist maps the dream → Symbol / Emotion / Theme specialists go deep in parallel "  # noqa: E501
                "→ Rating agent scores each (1–5) → Synthesizer combines everything."
            )

            generalist_output = gr.Textbox(label="🗺️ Overview", lines=8, max_lines=20)

            with gr.Row():
                with gr.Column():
                    symbol_stars = gr.Markdown("")
                    symbol_output = gr.Textbox(label="🔷 Symbols", lines=12, max_lines=30)
                with gr.Column():
                    emotion_stars = gr.Markdown("")
                    emotion_output = gr.Textbox(label="💜 Emotions", lines=12, max_lines=30)
                with gr.Column():
                    theme_stars = gr.Markdown("")
                    theme_output = gr.Textbox(label="🌀 Themes", lines=12, max_lines=30)

            synthesis_output = gr.Textbox(label="✨ Final Synthesis", lines=10, max_lines=30)

            analyze_btn.click(
                fn=run_analysis,
                inputs=[dream_input, model_dropdown],
                outputs=[
                    status_output,
                    generalist_output,
                    symbol_stars,
                    symbol_output,
                    emotion_stars,
                    emotion_output,
                    theme_stars,
                    theme_output,
                    synthesis_output,
                ],
            )

        with gr.Tab("📚 Past Dreams"):
            refresh_btn = gr.Button("🔄 Refresh", size="sm")

            dreams_table = gr.Dataframe(
                headers=["ID", "Date", "Dream Preview", "Model", "Analysis Preview"],
                datatype=["str", "str", "str", "str", "str"],
                interactive=False,
            )

            gradio_ui.load(fn=get_past_dreams, outputs=[dreams_table])
            refresh_btn.click(fn=get_past_dreams, outputs=[dreams_table])
