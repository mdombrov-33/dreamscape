from loguru import logger

from app.agents.base_agent import BaseAgent
from app.core.llm_client import generate, generate_stream

SYSTEM_PROMPT = """You are a dream theme analyst. You specialize exclusively in the psychological and life themes in dreams.

You have been given a first-pass analysis of a dream. Your job is to go significantly deeper on the themes only.

Explore:
- The core life themes this dream is engaging with (identity, control, loss, growth, relationships, etc.)
- What each theme suggests about the dreamer's waking life situation
- How the themes relate to each other — are they in conflict or reinforcing?
- What the dream might be trying to work through or resolve
- Relevant psychological frameworks if they genuinely fit (don't force them)

Write in flowing prose. Be specific to this dream, not generic. 3-4 paragraphs maximum."""  # noqa: E501


class ThemeSpecialist(BaseAgent):
    """Deep-dives on psychological themes using the generalist output as foundation."""

    @property
    def name(self) -> str:
        return "theme_specialist"

    @property
    def agent_type(self) -> str:
        return "specialist"

    async def analyze(self, dream_content: str, context: str | None = None) -> str:
        logger.info(f"ThemeSpecialist analyzing with {self.model}")
        prompt = (
            f'Dream:\n"{dream_content}"\n\n'
            f"First-pass analysis:\n{context}\n\n"
            "Provide a deep thematic analysis."
        )
        return await generate(model=self.model, prompt=prompt, system=SYSTEM_PROMPT)

    async def analyze_stream(self, dream_content: str, context: str | None = None):
        logger.info(f"ThemeSpecialist streaming with {self.model}")
        prompt = (
            f'Dream:\n"{dream_content}"\n\n'
            f"First-pass analysis:\n{context}\n\n"
            "Provide a deep thematic analysis."
        )
        async for chunk in generate_stream(model=self.model, prompt=prompt, system=SYSTEM_PROMPT):
            yield chunk
