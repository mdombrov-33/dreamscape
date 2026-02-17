AVAILABLE_MODELS: list[tuple[str, str]] = [
    ("Qwen 2.5 7B", "ollama/qwen2.5:7b"),
    ("GPT-5 Nano", "openrouter/openai/gpt-5-nano"),
    ("GPT-5.2", "openrouter/openai/gpt-5.2"),
    ("Claude Haiku 4.5", "openrouter/anthropic/claude-haiku-4.5"),
    ("Claude Sonnet 4.5", "openrouter/anthropic/claude-sonnet-4.5"),
    ("Gemini 3 Flash", "openrouter/google/gemini-3-flash-preview"),
]

MODEL_MAP: dict[str, str] = {label: model for label, model in AVAILABLE_MODELS}

MODEL_LABELS: list[str] = [label for label, _ in AVAILABLE_MODELS]

DEFAULT_MODEL_LABEL = "Qwen 2.5 7B"
DEFAULT_MODEL = "ollama/qwen2.5:7b"

# Model hierarchy (weaker → stronger) — used for future manual retry / comparison features
MODEL_ESCALATION: dict[str, str] = {
    "ollama/qwen2.5:7b":                        "openrouter/openai/gpt-5-nano",
    "openrouter/openai/gpt-5-nano":             "openrouter/anthropic/claude-haiku-4.5",
    "openrouter/google/gemini-3-flash-preview": "openrouter/anthropic/claude-haiku-4.5",
    "openrouter/anthropic/claude-haiku-4.5":    "openrouter/anthropic/claude-sonnet-4.5",
    # claude-sonnet-4.5 and gpt-5.2 are top of chain
}
