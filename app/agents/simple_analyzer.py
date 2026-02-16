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
        system_prompt = """You are a dream analyst. Analyze dreams and provide:
1. Key symbols and their meanings
2. Emotional themes
3. Possible interpretations
4. Connections to waking life

Be insightful but concise. Format your response clearly."""

        user_prompt = f"""Analyze this dream:

{dream_content}

Provide a thoughtful analysis covering symbols, emotions, and meaning."""

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
