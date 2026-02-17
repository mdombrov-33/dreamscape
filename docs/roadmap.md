# Dreamscape Roadmap

## Vision

A collective dream analysis platform. Every dream submitted is analyzed by a multi-agent pipeline, tagged with structured labels, and embedded into a vector space. Over time the system builds a shared dream atlas: you can find semantically similar dreams, explore recurring symbols across all submissions, and see what themes cluster together — all anonymous, no auth required.

The multi-agent pipeline is the extraction layer. Specialists aren't just commentators — they produce structured signal (tags, emotion labels, theme categories) that feeds the collective database.

## Full Pipeline

```
Dream
  ↓
Generalist          → structured overview (symbols, emotions, themes)   [streams live]
  ↓
Symbol Specialist ──┐
Emotion Specialist ─┼── parallel, each streams into its own panel      [streams live]
Theme Specialist  ──┘
  ↓
Rating Agent        → scores each specialist 1-5 (informational only)
  ↓
Synthesizer         → final interpretation                              [streams live]
  ↓
Tag Extractor       → ["water", "falling", "anxiety", ...]             (coming)
  ↓
Embedder            → pgvector embedding of full analysis              (coming)
```

All rows in `analyses` table: `dream_id`, `agent_name`, `agent_type`, `model_used`, `content`, `score`.

---

## Phase 1: MVP ✅ COMPLETE

- [x] Docker Compose (PostgreSQL + pgvector + Redis)
- [x] FastAPI + SQLAlchemy + Alembic
- [x] Dream and Analysis DB models
- [x] CRUD API for dreams
- [x] BaseAgent abstract class with model parameter
- [x] GeneralistAgent with structured section output
- [x] LiteLLM client (Ollama + OpenRouter)
- [x] 6 available models in config
- [x] Gradio UI with model dropdown

---

## Phase 2: Multi-Agent Pipeline ✅ COMPLETE

- [x] Symbol / Emotion / Theme specialist agents
- [x] SynthesizerAgent
- [x] RatingAgent (LLM-as-a-judge, scores 1-5, informational)
- [x] LangGraph workflow (generalist → specialists → rating → synthesizer)
- [x] `score` column on analyses table
- [x] Generalist streams live token by token
- [x] Specialists stream in parallel via SSE, each into its own panel
- [x] Synthesizer streams live after specialists complete
- [x] Scores shown per panel after rating finishes

**Decision log:**
- Automatic retry on low scores was removed — LLM judging LLM is unreliable, adds latency, escalates silently to cloud. Scores are kept as display-only signal.
- Manual retry button is planned for Phase 3 (user-triggered, explicit).
- Streaming uses SSE (`text/event-stream`) on `/stream-analyze` endpoint. Gradio reads via `httpx` + `iter_lines()`.

---

## Phase 3: Collective Layer 🔄 NEXT

### 3.1 Tag Extraction

After synthesis, a lightweight agent extracts 3–5 structured tags from the dream:
```json
{"symbols": ["water", "bridge"], "emotions": ["anxiety", "wonder"], "themes": ["transition"]}
```
Store as `tags` JSONB column on dreams table (or separate tags table for querying).
This is structured output — agent returns JSON, not prose.

### 3.2 Embeddings + pgvector

Embed the full analysis (or synthesis) with a text embedding model.
pgvector is already in the stack (`pgvector/pgvector:pg18`).

Add `embedding` vector column to dreams table. After each analysis, generate and store embedding.

Enables:
- `GET /dreams/{id}/similar` — top-5 semantically similar dreams
- UI: "Similar dreams" section on analysis page

### 3.3 Explore Tab

New Gradio tab showing collective patterns:
- Tag cloud of most common symbols / emotions / themes
- Bar charts: most frequent tags this week / all time
- "Dreams about water" — click a tag, see all matching dreams
- Cluster view: dreams grouped by semantic similarity

### 3.4 Manual Retry

Low-scored analyses (shown with score badge in UI) get a "Retry with stronger model" button.
Calls a new endpoint: `POST /dreams/{id}/analyses/{analysis_id}/retry?model=xxx`
Creates a new analysis row, updates the panel.

---

## Phase 4: Optional / Future

- **Per-agent model selection** — override global model per agent in UI
- **Cost tracking** — LiteLLM returns token counts; store `tokens_in`, `tokens_out` per analysis; calculate cost from known pricing
- **Batch export** — CSV/JSON of dreams, analyses, scores, tags
- **Prompt experimentation** — A/B different prompts per agent, compare outputs side by side

---

## Current Status

**Done:** Phase 1 + Phase 2 fully complete. Pipeline streams live. Scores displayed per panel.

**Next:** Phase 3.1 — tag extraction agent. Then 3.2 embeddings. Then 3.3 Explore tab.
