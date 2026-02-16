import httpx
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


class OllamaClient:
    """Client for interacting with local Ollama instance."""

    def __init__(self, base_url: str | None = None):
        """Initialize Ollama client.

        Args:
            base_url: Ollama API endpoint (default: from env or http://localhost:11434)
        """
        import os

        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.client = httpx.AsyncClient(timeout=120.0)  # 2 min timeout for LLM

    async def generate(
        self,
        model: str,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate text using Ollama (non-streaming).

        Args:
            model: Model name (e.g., "qwen2.5:7b")
            prompt: User prompt
            system: Optional system prompt
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)

        Returns:
            Generated text response
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        if system:
            payload["system"] = system

        logger.info(f"Calling Ollama model: {model}")

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            return result["response"]

        except httpx.HTTPError as e:
            logger.error(f"Ollama API error: {e}")
            raise

    async def generate_stream(
        self,
        model: str,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
    ):
        """
        Generate text using Ollama with streaming (yields tokens as they come).

        Args:
            model: Model name (e.g., "qwen2.5:7b")
            prompt: User prompt
            system: Optional system prompt
            temperature: Sampling temperature

        Yields:
            Text chunks as they are generated
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
            },
        }

        if system:
            payload["system"] = system

        logger.info(f"Calling Ollama model (streaming): {model}")

        try:
            async with self.client.stream("POST", url, json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line:
                        import json

                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]  # Yield each token

        except httpx.HTTPError as e:
            logger.error(f"Ollama API error: {e}")
            raise

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
_ollama_client: OllamaClient | None = None


def get_ollama_client() -> OllamaClient:
    """Get or create Ollama client singleton."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client
