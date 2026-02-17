from loguru import logger

from app.agents.base_agent import BaseAgent
from app.core.llm_client import generate, generate_stream

SYSTEM_PROMPT = """You are a dream emotion analyst. You specialize exclusively in the emotional landscape of dreams.

You have been given a first-pass analysis of a dream. Your job is to go significantly deeper on the emotions only.

Explore:
- The explicit and implicit emotions present in the dream
- Emotional contradictions or tensions (e.g., fear mixed with excitement)
- What the emotional tone reveals about the dreamer's current inner state
- How the emotions shift throughout the dream narrative
- What unresolved feelings or needs these emotions might point to

Write in flowing prose. Be specific to this dream, not generic. 3-4 paragraphs maximum."""  # noqa: E501


class EmotionSpecialist(BaseAgent):
    """Deep-dives on emotional landscape using the generalist output as foundation."""

    @property
    def name(self) -> str:
        return "emotion_specialist"

    @property
    def agent_type(self) -> str:
        return "specialist"

    async def analyze(self, dream_content: str, context: str | None = None) -> str:
        logger.info(f"EmotionSpecialist analyzing with {self.model}")
        prompt = (
            f'Dream:\n"{dream_content}"\n\n'
            f"First-pass analysis:\n{context}\n\n"
            "Provide a deep emotional analysis."
        )
        return await generate(model=self.model, prompt=prompt, system=SYSTEM_PROMPT)

    async def analyze_stream(self, dream_content: str, context: str | None = None):
        logger.info(f"EmotionSpecialist streaming with {self.model}")
        prompt = (
            f'Dream:\n"{dream_content}"\n\n'
            f"First-pass analysis:\n{context}\n\n"
            "Provide a deep emotional analysis."
        )
        async for chunk in generate_stream(model=self.model, prompt=prompt, system=SYSTEM_PROMPT):
            yield chunk
