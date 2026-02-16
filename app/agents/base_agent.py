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
        Analyze a dream and return insights.

        Args:
            dream_content: The dream text to analyze

        Returns:
            Analysis result as text
        """
        pass
