# Dreamscape Roadmap

## Vision

Build a multi-agent dream analysis pipeline where each agent can run a different model. Track which models and configurations produce the best analysis. Learn LangGraph and LiteLLM in the process.

## Agent Workflow

```
Dream → Generalist → [Symbol, Emotion, Theme] (parallel) → Synthesizer
```

Each agent stores: `agent_name`, `agent_type`, `model_used`, `content` in the database.

---

## Phase 1: MVP ✅ COMPLETE

- [x] Docker Compose (PostgreSQL)
- [x] FastAPI + SQLAlchemy + Alembic
- [x] Dream and Analysis DB models (with agent_type, model_used)
- [x] CRUD API for dreams
- [x] BaseAgent abstract class
- [x] SimpleDreamAnalyzer (generalist, structured output)
- [x] LiteLLM client (Ollama + OpenRouter)
- [x] 6 available models in config
- [x] Gradio UI with model dropdown and streaming
- [x] Analysis saved to DB with model info

---

## Phase 2: Multi-Agent Workflow 🔄 IN PROGRESS

### 2.1 Specialist Agents

Files to create:
- `app/agents/symbol_specialist.py`
- `app/agents/emotion_specialist.py`
- `app/agents/theme_specialist.py`

Each specialist:
- Receives dream + generalist output as `context`
- Focuses only on its domain
- Uses the same model passed from UI (or we add per-agent dropdowns later)

### 2.2 Synthesizer Agent

File: `app/agents/synthesizer_agent.py`

- Receives dream + all specialist outputs as context
- Writes a final integrated interpretation
- Good candidate for prompt caching (context will be 1000+ tokens)

### 2.3 LangGraph Workflow

File: `app/workflows/dream_analysis.py`

```python
Dream → Generalist → asyncio.gather(Symbol, Emotion, Theme) → Synthesizer
```

- LangGraph handles state between nodes
- Parallel execution of specialists
- Synthesizer waits for all three to finish

### 2.4 Updated UI

- 4 output panels: Symbol / Emotion / Theme / Synthesis
- Status indicators per agent (⏳ working → ✅ done)
- Stream specialists sequentially or show all on completion
- Optional: per-agent model dropdowns (global dropdown stays as default)

---

## Phase 3: Evaluation Framework

### 3.1 Rating System
- Add 1-5 star rating per analysis
- Store in DB with `analysis_id` and optional `feedback_text`

### 3.2 Cost Tracking
- LiteLLM returns token counts in response metadata
- Store `tokens_in`, `tokens_out`, calculate cost per analysis
- Display cost in UI

### 3.3 Analytics Dashboard
- New Gradio tab: "📊 Analytics"
- Avg rating per model
- Cost per model
- Best performing configurations

---

## Phase 4: Optional / Future

- **Embeddings** — store dream embeddings in pgvector, find similar dreams
- **Per-agent model selection** — dropdown per agent in UI
- **Prompt caching** — for Anthropic models, cache system prompts when context gets large (synthesizer is the main candidate)
- **Auth + personal tracking** — track patterns across your own dreams over time
- **Batch export** — CSV/JSON export of dreams and analyses

---

## Current Status

**Done:**
- Phase 1 fully complete
- LiteLLM integrated
- Model dropdown in UI working
- Generalist prompt outputs structured sections for specialist handoff

**Next:**
- Build 3 specialist agents
- Build synthesizer agent
- Wire LangGraph workflow
- Update UI to show per-agent panels
