from loguru import logger

from app.agents.base_agent import BaseAgent
from app.core.llm_client import generate, generate_stream

SYSTEM_PROMPT = """You are a dream analyst doing a first-pass read of a dream. Your job is to map out the landscape so other specialists can go deeper.

Structure your response with these exact sections:

Overview: A few sentences on the overall feel and narrative of the dream.
Key Symbols: List the main symbols you notice and a brief note on each.
Emotional Tone: What emotions are present or implied? What is the dreamer feeling?
Themes: The core psychological or life themes this dream seems to be touching on.

Be concise. Each section should be 2-4 sentences. No bullet points inside sections, just prose."""  # noqa: E501


class GeneralistAgent(BaseAgent):
    """First-pass dream analyst. Produces structured output for specialists."""

    @property
    def name(self) -> str:
        return "generalist"

    @property
    def agent_type(self) -> str:
        return "generalist"

    async def analyze(self, dream_content: str, context: str | None = None) -> str:
        logger.info(f"GeneralistAgent analyzing with {self.model}")
        return await generate(
            model=self.model,
            prompt=f'Here\'s the dream:\n\n"{dream_content}"\n\nProvide a structured first-pass analysis.',  # noqa: E501
            system=SYSTEM_PROMPT,
        )

    async def analyze_stream(self, dream_content: str, context: str | None = None):
        logger.info(f"GeneralistAgent streaming with {self.model}")
        async for chunk in generate_stream(
            model=self.model,
            prompt=f'Here\'s the dream:\n\n"{dream_content}"\n\nProvide a structured first-pass analysis.',  # noqa: E501
            system=SYSTEM_PROMPT,
        ):
            yield chunk
