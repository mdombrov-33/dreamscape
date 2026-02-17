import os

import litellm
from litellm import CustomStreamWrapper, ModelResponse
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

litellm.drop_params = True  # Ignore unsupported params per model


def _build_messages(prompt: str, system: str | None) -> list[dict]:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return messages


def _configure_provider(model: str) -> None:
    if model.startswith("openrouter/") and settings.openrouter_api_key:
        os.environ["OPENROUTER_API_KEY"] = settings.openrouter_api_key
    elif model.startswith("ollama/"):
        os.environ["OLLAMA_API_BASE"] = settings.ollama_base_url


async def generate(
    model: str,
    prompt: str,
    system: str | None = None,
    temperature: float = 0.7,
) -> str:
    """Generate text from any supported model."""
    _configure_provider(model)
    messages = _build_messages(prompt, system)

    logger.info(f"LLM call: {model}")

    response: ModelResponse = await litellm.acompletion(  # type: ignore[assignment]
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""  # type: ignore[union-attr]


async def generate_stream(
    model: str,
    prompt: str,
    system: str | None = None,
    temperature: float = 0.7,
):
    """Generate text from any supported model with streaming."""
    _configure_provider(model)
    messages = _build_messages(prompt, system)

    logger.info(f"LLM stream: {model}")

    response: CustomStreamWrapper = await litellm.acompletion(  # type: ignore[assignment]
        model=model,
        messages=messages,
        temperature=temperature,
        stream=True,
    )

    async for chunk in response:
        content = chunk.choices[0].delta.content  # type: ignore[union-attr]
        if content:
            yield content
