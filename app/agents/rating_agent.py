import json

from loguru import logger

from app.agents.base_agent import BaseAgent
from app.core.llm_client import generate

SYSTEM_PROMPT = """You are evaluating the quality of a dream analysis. Be honest and critical.

Rate the analysis on three dimensions:
- depth: Does it go beyond the obvious? Does it explore nuance? (1-5)
- relevance: Is it grounded in the actual dream content, not generic? (1-5)
- insight: Does it offer genuine insight the dreamer couldn't easily see themselves? (1-5)

Respond with ONLY valid JSON, no explanation, no markdown:
{"depth": <1-5>, "relevance": <1-5>, "insight": <1-5>}"""


class RatingAgent(BaseAgent):
    """LLM-as-a-judge. Scores specialist analyses on depth, relevance, and insight."""

    @property
    def name(self) -> str:
        return "rating_agent"

    @property
    def agent_type(self) -> str:
        return "judge"

    async def analyze(self, dream_content: str, context: str | None = None) -> str:
        """Rate an analysis. dream_content = original dream, context = analysis to rate."""
        logger.info(f"RatingAgent evaluating with {self.model}")
        prompt = f'Dream:\n"{dream_content}"\n\nAnalysis to evaluate:\n{context}'
        return await generate(model=self.model, prompt=prompt, system=SYSTEM_PROMPT)

    async def analyze_stream(self, dream_content: str, context: str | None = None):
        result = await self.analyze(dream_content, context)
        yield result

    def parse_scores(self, raw: str) -> dict[str, int]:
        """Parse JSON scores. Returns {depth, relevance, insight} defaulting to 3 on failure."""
        try:
            cleaned = raw.strip()
            if "```" in cleaned:
                cleaned = cleaned.split("```")[1].replace("json", "").strip()
            scores = json.loads(cleaned)
            return {
                "depth": max(1, min(5, int(scores.get("depth", 3)))),
                "relevance": max(1, min(5, int(scores.get("relevance", 3)))),
                "insight": max(1, min(5, int(scores.get("insight", 3)))),
            }
        except (json.JSONDecodeError, ValueError, KeyError):
            logger.warning(f"Failed to parse rating scores from: {raw!r}")
            return {"depth": 3, "relevance": 3, "insight": 3}

    def average_score(self, scores: dict[str, int]) -> int:
        return round(sum(scores.values()) / len(scores))
