from abc import ABC, abstractmethod

from app.core.models_config import DEFAULT_MODEL


class BaseAgent(ABC):
    """Base class for all dream analysis agents."""

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent identifier stored in DB."""
        pass

    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Role in workflow: 'generalist' | 'specialist' | 'synthesizer'"""
        pass

    @abstractmethod
    async def analyze(self, dream_content: str, context: str | None = None) -> str:
        """Analyze dream, return full text. context = generalist output for specialists."""
        pass

    @abstractmethod
    async def analyze_stream(self, dream_content: str, context: str | None = None):
        """Analyze dream with streaming. Yields text chunks."""
        pass
