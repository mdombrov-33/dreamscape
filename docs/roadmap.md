# Dreamscape Roadmap

## Vision

A multi-agent dream analysis pipeline where a rating agent (LLM-as-a-judge) automatically scores each specialist output. Weak analyses get retried with a stronger model. Over time the system builds a real dataset: which models work best at which roles, at what cost.

## Full Pipeline

```
Dream
  ↓
Generalist          → structured output (symbols, emotions, themes, overview)
  ↓
Symbol Specialist ──┐
Emotion Specialist ─┼── parallel, get generalist output as context
Theme Specialist  ──┘
  ↓
Rating Agent        → scores each specialist 1-5 (depth, relevance, insight)
                      score < threshold → retry with escalation model
  ↓
Synthesizer         → receives best version of each, writes final interpretation
```

All rows in `analyses` table: `dream_id`, `agent_name`, `agent_type`, `model_used`, `content`, `score`.

## Model Escalation Chain

```python
ESCALATION = {
    "ollama/qwen2.5:7b":                     "openrouter/openai/gpt-5-nano",
    "openrouter/openai/gpt-5-nano":          "openrouter/anthropic/claude-haiku-4.5",
    "openrouter/anthropic/claude-haiku-4.5": "openrouter/anthropic/claude-sonnet-4.5",
}
```

Only failing analyses get escalated. Both versions saved to DB.

---

## Phase 1: MVP ✅ COMPLETE

- [x] Docker Compose (PostgreSQL)
- [x] FastAPI + SQLAlchemy + Alembic
- [x] Dream and Analysis DB models (agent_type, model_used)
- [x] CRUD API for dreams
- [x] BaseAgent abstract class with model parameter
- [x] SimpleDreamAnalyzer (generalist, structured section output)
- [x] LiteLLM client (Ollama + OpenRouter)
- [x] 6 available models in config
- [x] Gradio UI with model dropdown and streaming

---

## Phase 2: Multi-Agent Pipeline 🔄 IN PROGRESS

### 2.1 Specialist Agents ← NEXT

Files: `app/agents/symbol_specialist.py`, `emotion_specialist.py`, `theme_specialist.py`

Each specialist:
- `agent_type = "specialist"`
- Receives `context` = generalist output
- Prompt focuses only on its domain
- Goes deeper than the generalist's section on that topic

### 2.2 Synthesizer Agent

File: `app/agents/synthesizer_agent.py`

- `agent_type = "synthesizer"`
- Receives all specialist outputs as context
- Writes final integrated interpretation
- Good candidate for prompt caching (context will be 1000+ tokens)

### 2.3 Rating Agent (LLM-as-a-judge)

File: `app/agents/rating_agent.py`

- `agent_type = "judge"`
- Not a dream analyst — evaluates quality of other agents' outputs
- Input: original dream + one specialist's analysis
- Output: JSON scores `{"depth": 4, "relevance": 3, "insight": 4}`
- Scores saved to `analyses` table (add `score` column)
- Judge model stays fixed (e.g. Claude Haiku) regardless of which model did the analysis — consistency matters

### 2.4 LangGraph Workflow

File: `app/workflows/dream_analysis.py`

**The entire pipeline is one LangGraph graph** — not just the retry part. Specialists are nodes in the graph too. This way the whole flow is in one place, state is explicit, and conditional routing is built into the graph edges.

```
generalist_node
      ↓
specialists_node   (symbol, emotion, theme run in parallel inside this node)
      ↓
rating_node        (judge scores each specialist output)
      ↓
[conditional edges]
  score ≥ 3  →  synthesizer_node
  score < 3  →  retry_node  →  rating_node  →  synthesizer_node
```

State:
```python
class DreamAnalysisState(TypedDict):
    dream_id: int
    dream: str
    model: str
    generalist: str
    symbol: str
    emotion: str
    theme: str
    scores: dict        # {"symbol": 4, "emotion": 2, "theme": 3}
    retried: set        # which agents already retried (avoid infinite loop)
    synthesis: str
```

**UI shows the graph executing in real time:**
```
[✅ Generalist]
[✅ Symbol 4/5]  [⏳ Emotion...]  [✅ Theme 3/5]
[🔄 Emotion retried with Claude Haiku → ✅ 4/5]
[⏳ Synthesizer...]
```

Each panel fills in as its node completes. LangGraph emits events during execution — we use those to update the UI progressively.

### 2.5 DB Migration

Add `score` column to `analyses` table:
```python
score: Mapped[int | None] = mapped_column(Integer, nullable=True)
```

Nullable — only rating agent writes it, all other agents leave it null.

### 2.6 Updated UI

- Show each agent's output in its own panel
- Status indicators per agent (⏳ → ✅)
- Show score badge next to specialist output
- Show which analyses were retried and with which model

---

## Phase 3: Analytics

### 3.1 Analytics Dashboard (new Gradio tab)

- Average score per model per agent type
- Escalation rate per model ("Qwen gets escalated 55% of the time on emotion")
- Cost per dream by configuration
- Best performing config per agent role

### 3.2 Cost Tracking

- LiteLLM returns token counts in response metadata
- Store `tokens_in`, `tokens_out` per analysis
- Calculate cost from known model pricing

---

## Phase 4: Optional / Future

- **Embeddings** — pgvector, find similar dreams
- **Per-agent model selection** — override global model per agent in UI
- **Auth + personal tracking** — patterns across your own dreams over time
- **Prompt caching** — Anthropic cache_control on synthesizer (context hits 1000+ tokens)
- **Batch export** — CSV/JSON of dreams, analyses, scores

---

## Current Status

**Done:**
- Phase 1 fully complete
- LiteLLM integrated, model dropdown in UI, structured generalist output

**Next:**
- Specialist agents (symbol, emotion, theme)
- Synthesizer agent
- Rating agent
- Add `score` column to DB
- LangGraph workflow
- Update UI for multi-agent display
