from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Abstract base class for dream analysis agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return agent name (e.g., 'simple_analyzer')."""
        pass

    @abstractmethod
    async def analyze(self, dream_content: str) -> str:
        """
        Analyze a dream and return insights (non-streaming).

        Args:
            dream_content: The dream text to analyze

        Returns:
            Analysis result as text
        """
        pass

    @abstractmethod
    async def analyze_stream(self, dream_content: str):
        """
        Analyze a dream and yield insights as they are generated (streaming).

        Args:
            dream_content: The dream text to analyze

        Yields:
            Text chunks as they are generated
        """
        pass
