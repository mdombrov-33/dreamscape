from loguru import logger

from app.agents.base_agent import BaseAgent
from app.core.llm_client import generate, generate_stream

SYSTEM_PROMPT = """You are the final interpreter in a multi-agent dream analysis pipeline.

You have received a first-pass analysis plus three specialist analyses covering symbols, emotions, and themes in depth.

Your job: synthesize everything into one final interpretation. Don't repeat or summarize what the specialists said — find the connections between layers. What emerges when the symbol, emotional, and thematic readings are brought together? What does the dream mean as a whole?

Be specific to this dream. No generic life-coaching, no "ask yourself", no advice. Pure interpretation — what the dream reveals, not what the dreamer should do. 2-3 paragraphs maximum."""  # noqa: E501


class SynthesizerAgent(BaseAgent):
    """Combines all specialist outputs into a final interpretation."""

    @property
    def name(self) -> str:
        return "synthesizer"

    @property
    def agent_type(self) -> str:
        return "synthesizer"

    async def analyze(self, dream_content: str, context: str | None = None) -> str:
        logger.info(f"SynthesizerAgent analyzing with {self.model}")
        prompt = (
            f'Dream:\n"{dream_content}"\n\n'
            f"Specialist analyses:\n{context}\n\n"
            "Write the final synthesis."
        )
        return await generate(model=self.model, prompt=prompt, system=SYSTEM_PROMPT)

    async def analyze_stream(self, dream_content: str, context: str | None = None):
        logger.info(f"SynthesizerAgent streaming with {self.model}")
        prompt = (
            f'Dream:\n"{dream_content}"\n\n'
            f"Specialist analyses:\n{context}\n\n"
            "Write the final synthesis."
        )
        async for chunk in generate_stream(model=self.model, prompt=prompt, system=SYSTEM_PROMPT):
            yield chunk
