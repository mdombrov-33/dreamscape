import gradio as gr

from app.core.models_config import DEFAULT_MODEL_LABEL, MODEL_LABELS
from app.ui.handlers import get_past_dreams, run_analysis
from app.ui.whisper import transcribe_audio

with gr.Blocks(theme="soft", title="Dreamscape") as gradio_ui:
    gr.Markdown("# 🌙 Dreamscape")

    with gr.Tabs():
        with gr.Tab("✨ New Dream"):

            with gr.Row():
                model_dropdown = gr.Dropdown(
                    label="Model",
                    choices=MODEL_LABELS,
                    value=DEFAULT_MODEL_LABEL,
                    scale=2,
                )
                status_output = gr.Textbox(
                    label="Status", lines=1, max_lines=1, scale=3, interactive=False
                )

            with gr.Accordion("🎙️ Record instead of typing", open=False):
                with gr.Row():
                    mic_input = gr.Audio(sources=["microphone"], type="numpy", label="")
                    transcribe_btn = gr.Button("📝 Transcribe", size="sm", scale=0)

            dream_input = gr.Textbox(
                label="Dream",
                placeholder="I was flying through a dark forest, when suddenly...",
                lines=5,
                max_lines=20,
            )

            analyze_btn = gr.Button("🔮 Analyze Dream", variant="primary", size="lg")

            transcribe_btn.click(fn=transcribe_audio, inputs=[mic_input], outputs=[dream_input])

            with gr.Row():
                generalist_output = gr.Textbox(label="🗺️ Overview", lines=6, max_lines=15, scale=1)
                synthesis_output  = gr.Textbox(label="✨ Synthesis", lines=6, max_lines=15, scale=1)

            with gr.Row():
                with gr.Column():
                    symbol_stars  = gr.Markdown("")
                    symbol_output = gr.Textbox(label="🔷 Symbols", lines=8, max_lines=20)
                with gr.Column():
                    emotion_stars  = gr.Markdown("")
                    emotion_output = gr.Textbox(label="💜 Emotions", lines=8, max_lines=20)
                with gr.Column():
                    theme_stars  = gr.Markdown("")
                    theme_output = gr.Textbox(label="🌀 Themes", lines=8, max_lines=20)

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
