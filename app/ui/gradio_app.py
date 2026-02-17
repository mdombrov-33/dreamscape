import asyncio

import gradio as gr
from loguru import logger
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.agents.simple_analyzer import SimpleDreamAnalyzer
from app.core.config import get_settings
from app.core.models_config import DEFAULT_MODEL_LABEL, MODEL_LABELS, MODEL_MAP
from app.db.models.dream import Dream

settings = get_settings()

sync_engine = create_engine(settings.sync_database_url)
SyncSessionLocal = sessionmaker(bind=sync_engine)


def analyze_dream_streaming(dream_text: str, model_label: str):
    if not dream_text or len(dream_text.strip()) < 10:
        yield "❌ Please enter a longer dream (at least 10 characters)"
        return

    model = MODEL_MAP.get(model_label, MODEL_MAP[DEFAULT_MODEL_LABEL])
    logger.info(f"Analyzing dream with {model_label}: {dream_text[:50]}...")

    try:
        with SyncSessionLocal() as db:
            dream = Dream(content=dream_text)
            db.add(dream)
            db.commit()
            db.refresh(dream)
            dream_id = dream.id

        agent = SimpleDreamAnalyzer(model=model)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        full_analysis = ""

        try:
            async_gen = agent.analyze_stream(dream_text)

            while True:
                try:
                    chunk = loop.run_until_complete(async_gen.__anext__())
                    full_analysis += chunk
                    yield full_analysis
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

        with SyncSessionLocal() as db:
            from app.db.models.analysis import Analysis

            analysis = Analysis(
                dream_id=dream_id,
                agent_name=agent.name,
                agent_type=agent.agent_type,
                model_used=agent.model,
                content=full_analysis,
            )
            db.add(analysis)
            db.commit()

        logger.info(f"Dream {dream_id} analyzed and saved with {model}")

    except Exception as e:
        logger.error(f"UI analysis error: {e}")
        yield f"❌ Error: {str(e)}"


def get_past_dreams():
    try:
        with SyncSessionLocal() as db:
            stmt = select(Dream).order_by(Dream.created_at.desc()).limit(50)
            dreams = db.execute(stmt).scalars().all()

            if not dreams:
                return [["No dreams yet", "", "", "", ""]]

            rows = []
            for dream in dreams:
                analysis_preview = ""
                model_used = ""
                if dream.analyses:
                    first = dream.analyses[0]
                    analysis_preview = first.content[:100] + "..."
                    model_used = first.model_used

                rows.append([
                    str(dream.id),
                    dream.created_at.strftime("%Y-%m-%d %H:%M"),
                    dream.content[:100] + ("..." if len(dream.content) > 100 else ""),
                    model_used,
                    analysis_preview,
                ])

            return rows

    except Exception as e:
        logger.error(f"UI error fetching dreams: {e}")
        return [[f"Error: {str(e)}", "", "", "", ""]]


with gr.Blocks(
    theme="soft",
    title="Dreamscape - AI Dream Journal",
) as gradio_ui:
    gr.Markdown(
        """
        # 🌙 Dreamscape
        ### AI-Powered Dream Analysis
        """
    )

    with gr.Tabs():
        with gr.Tab("✨ New Dream"):
            model_dropdown = gr.Dropdown(
                label="Model",
                choices=MODEL_LABELS,
                value=DEFAULT_MODEL_LABEL,
            )

            dream_input = gr.Textbox(
                label="Dream Description",
                placeholder="I was flying through a dark forest, when suddenly...",
                lines=8,
                max_lines=20,
            )

            analyze_btn = gr.Button("🔮 Analyze Dream", variant="primary", size="lg")

            gr.Markdown("### 🤖 Analysis")

            analysis_output = gr.Textbox(
                label="",
                placeholder="Your analysis will appear here as it's being generated...",
                lines=15,
                max_lines=30,
                show_label=False,
            )

            analyze_btn.click(
                fn=analyze_dream_streaming,
                inputs=[dream_input, model_dropdown],
                outputs=[analysis_output],
            )

        with gr.Tab("📚 Past Dreams"):
            gr.Markdown("### Dream Journal")

            refresh_btn = gr.Button("🔄 Refresh", size="sm")

            dreams_table = gr.Dataframe(
                headers=["ID", "Date", "Dream Preview", "Model", "Analysis Preview"],
                datatype=["str", "str", "str", "str", "str"],
                interactive=False,
            )

            gradio_ui.load(fn=get_past_dreams, outputs=[dreams_table])
            refresh_btn.click(fn=get_past_dreams, outputs=[dreams_table])
