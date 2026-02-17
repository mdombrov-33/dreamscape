from loguru import logger

from app.agents.base_agent import BaseAgent
from app.core.llm_client import generate, generate_stream

SYSTEM_PROMPT = """You are a dream symbol analyst. You specialize exclusively in the deep meaning of symbols.

You have been given a first-pass analysis of a dream. Your job is to go significantly deeper on the symbols only.

For each symbol identified, explore:
- Its archetypal or cultural meaning
- What it might represent personally for the dreamer
- How its specific state or behavior in the dream adds meaning (a locked door vs an open door)
- How it connects to other symbols present

Write in flowing prose. Be specific to this dream, not generic. 3-4 paragraphs maximum."""  # noqa: E501


class SymbolSpecialist(BaseAgent):
    """Deep-dives on dream symbols using the generalist output as foundation."""

    @property
    def name(self) -> str:
        return "symbol_specialist"

    @property
    def agent_type(self) -> str:
        return "specialist"

    async def analyze(self, dream_content: str, context: str | None = None) -> str:
        logger.info(f"SymbolSpecialist analyzing with {self.model}")
        prompt = (
            f'Dream:\n"{dream_content}"\n\n'
            f"First-pass analysis:\n{context}\n\n"
            "Provide a deep symbol analysis."
        )
        return await generate(model=self.model, prompt=prompt, system=SYSTEM_PROMPT)

    async def analyze_stream(self, dream_content: str, context: str | None = None):
        logger.info(f"SymbolSpecialist streaming with {self.model}")
        prompt = (
            f'Dream:\n"{dream_content}"\n\n'
            f"First-pass analysis:\n{context}\n\n"
            "Provide a deep symbol analysis."
        )
        async for chunk in generate_stream(model=self.model, prompt=prompt, system=SYSTEM_PROMPT):
            yield chunk
