from loguru import logger

from app.agents.base_agent import BaseAgent
from app.core.ollama import get_ollama_client


class SimpleDreamAnalyzer(BaseAgent):
    """Simple agent that analyzes dreams using Ollama."""

    def __init__(self, model: str = "qwen2.5:7b"):
        """
        Initialize the analyzer.

        Args:
            model: Ollama model to use
        """
        self.model = model
        self.ollama = get_ollama_client()

    @property
    def name(self) -> str:
        """Return agent name."""
        return "simple_analyzer"

    async def analyze(self, dream_content: str) -> str:
        """
        Analyze a dream and provide insights.

        Args:
            dream_content: The dream text

        Returns:
            Analysis with symbols, emotions, and interpretations
        """
        system_prompt = """You are a thoughtful dream analyst. Provide a natural, flowing analysis covering:
- Key symbols and what they might represent
- Emotional themes present in the dream
- Possible psychological interpretations
- Potential connections to waking life

Write in a warm, conversational style. Use minimal formatting - just write naturally as if speaking to the dreamer. Avoid excessive markdown, headers, or bullet points."""  # noqa: E501

        user_prompt = f"""Here's the dream:

"{dream_content}"

Please provide a thoughtful analysis in natural, flowing prose."""

        logger.info(f"Analyzing dream with {self.model}")

        try:
            analysis = await self.ollama.generate(
                model=self.model,
                prompt=user_prompt,
                system=system_prompt,
                temperature=0.7,
            )

            logger.info(f"Analysis complete ({len(analysis)} chars)")
            return analysis

        except Exception as e:
            logger.error(f"Dream analysis failed: {e}")
            return f"Analysis failed: {str(e)}"

    async def analyze_stream(self, dream_content: str):
        """
        Analyze a dream and yield insights as they are generated (streaming).

        Args:
            dream_content: The dream text

        Yields:
            Analysis chunks as they are generated
        """
        system_prompt = """You are a thoughtful dream analyst. Provide a natural, flowing analysis covering:
- Key symbols and what they might represent
- Emotional themes present in the dream
- Possible psychological interpretations
- Potential connections to waking life

Write in a warm, conversational style. Use minimal formatting - just write naturally as if speaking to the dreamer. Avoid excessive markdown, headers, or bullet points."""  # noqa: E501

        user_prompt = f"""Here's the dream:

"{dream_content}"

Please provide a thoughtful analysis in natural, flowing prose."""

        logger.info(f"Analyzing dream with {self.model} (streaming)")

        try:
            async for chunk in self.ollama.generate_stream(
                model=self.model,
                prompt=user_prompt,
                system=system_prompt,
                temperature=0.7,
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Dream analysis failed: {e}")
            yield f"Analysis failed: {str(e)}"
