# Dreamscape Development Roadmap

## Vision

A dream journal with multi-agent AI analysis and evaluation framework to measure which AI approaches work best for dream interpretation.

## Core User Flow

```
1. User logs dream → 2. AI agents analyze → 3. User sees analyses → 4. User rates quality → 5. System learns
```

### Detailed Flow

1. **User enters dream**: "I was flying over a city at night..."
2. **System stores dream**: PostgreSQL + generate embedding (pgvector)
3. **Multiple agents analyze** (in background):
   - Symbol Detector Agent: Identifies recurring symbols
   - Emotion Analyzer Agent: Detects emotional patterns
   - Insight Generator Agent: Deep psychological interpretation
4. **User sees all analyses** side-by-side in Gradio UI
5. **User rates** which analysis was most helpful (1-5 stars)
6. **Eval system tracks**:
   - Which agent got highest ratings?
   - Which prompts perform best?
   - Cost vs quality tradeoffs
7. **Semantic search**: Find similar past dreams by meaning

## Features

### Phase 1: MVP (Core Dream Journal)

**Goal**: Basic working dream journal with one AI agent

#### 1.1 Database Models & Migrations

- [ ] Create `Dream` model (id, content, date, user_id, embedding)
- [ ] Create `Analysis` model (id, dream_id, agent_name, content, created_at)
- [ ] Setup Alembic migrations
- [ ] Create initial migration

**Files to create**:

- `app/db/models/dream.py`
- `app/db/models/analysis.py`
- `alembic/` setup
- `alembic/versions/001_initial.py`

#### 1.2 Basic CRUD API

- [ ] POST /dreams - Create dream
- [ ] GET /dreams - List all dreams
- [ ] GET /dreams/{id} - Get dream with analyses
- [ ] Pydantic schemas for validation

**Files to create**:

- `app/schemas/dream.py` (DreamCreate, DreamRead)
- `app/api/v1/dreams.py` (routes)
- `app/services/dream_service.py` (business logic)

#### 1.3 First AI Agent (Simple)

- [ ] Create base agent interface
- [ ] Implement simple analysis agent (uses Ollama/qwen2.5)
- [ ] Trigger analysis on dream creation
- [ ] Store analysis result

**Files to create**:

- `app/agents/base_agent.py` (abstract class)
- `app/agents/simple_agent.py` (first implementation)
- `app/services/analysis_service.py`

#### 1.4 Simple Gradio UI

- [ ] Dream entry form
- [ ] Dream list view
- [ ] Analysis display
- [ ] Stream AI response in real-time

**Files to create**:

- `app/ui/gradio_app.py`
- Mount in FastAPI: `app.mount("/ui", gradio_app)`

**MVP Deliverable**: Enter dream → Get AI analysis → See in UI

---

### Phase 2: Multi-Agent System 🤖

**Goal**: Multiple agents analyze same dream, compare results

#### 2.1 Additional Agents

- [ ] Symbol detector agent (finds recurring symbols)
- [ ] Emotion analyzer agent (emotional tone)
- [ ] GPT-5 agent (high-quality insights)
- [ ] Claude agent (alternative perspective)

#### 2.2 Agent Orchestration (LangGraph)

- [ ] Setup LangGraph workflow
- [ ] Parallel agent execution
- [ ] Aggregate results

#### 2.3 UI Improvements

- [ ] Tabs for each agent's analysis
- [ ] Side-by-side comparison view
- [ ] Highlight differences

**Deliverable**: One dream → Multiple analyses from different agents

---

### Phase 3: Evaluation Framework 📊

**Goal**: Measure which agents/prompts work best

#### 3.1 User Ratings

- [ ] Add rating system (1-5 stars per analysis)
- [ ] Store ratings in `AnalysisRating` model
- [ ] UI for rating

#### 3.2 Quality Metrics

- [ ] LLM-as-judge evaluator (GPT-5 rates other analyses)
- [ ] Consistency evaluator (same dream → similar output?)
- [ ] Hallucination detector (are claims supported?)

#### 3.3 Eval Dashboard

- [ ] Agent performance leaderboard
- [ ] Cost vs quality charts
- [ ] Prompt comparison

**Files to create**:

- `app/evals/evaluators/quality_eval.py`
- `app/evals/evaluators/consistency_eval.py`
- `app/evals/metrics/rating_metrics.py`
- `app/ui/eval_dashboard.py`

**Deliverable**: Data on which agents perform best

---

### Phase 4: Semantic Search 🔍

**Goal**: Find similar dreams by meaning

#### 4.1 Embeddings

- [ ] Generate embeddings on dream creation (OpenAI/local model)
- [ ] Store in `dream.embedding` (pgvector)
- [ ] Index for fast search

#### 4.2 Search API

- [ ] POST /dreams/search - Semantic search endpoint
- [ ] Returns similar dreams by meaning
- [ ] Similarity score

#### 4.3 UI Integration

- [ ] Search bar in Gradio
- [ ] Similar dreams section
- [ ] "Dreams like this" suggestions

**Deliverable**: Search "falling nightmares" → Find similar dreams

---

### Phase 5: Advanced Features 🚀

#### 5.1 Background Jobs

- [ ] Setup arq (async task queue with Redis)
- [ ] Queue dream analysis (don't block API)
- [ ] Progress tracking

#### 5.2 Caching

- [ ] Redis cache for LLM responses
- [ ] Cache analyses (same dream → cached result)
- [ ] LiteLLM prompt caching

#### 5.3 Golden Dataset

- [ ] Curate test dreams with expected analyses
- [ ] Regression testing (did prompt change break quality?)
- [ ] Automated eval runs

#### 5.4 API Improvements

- [ ] Authentication (user accounts)
- [ ] Rate limiting
- [ ] Pagination
- [ ] Filtering/sorting

---

## Development Phases Summary

| Phase                    | Goal                            | Time Estimate |
| ------------------------ | ------------------------------- | ------------- |
| **Phase 1: MVP**         | Basic dream journal + one agent | 2-3 days      |
| **Phase 2: Multi-Agent** | Multiple agents, LangGraph      | 2-3 days      |
| **Phase 3: Evals**       | Evaluation framework            | 2-3 days      |
| **Phase 4: Search**      | Semantic search                 | 1-2 days      |
| **Phase 5: Advanced**    | Production features             | Ongoing       |

---

## Starting Point: Phase 1.1 - Database Models

**Next immediate steps:**

1. **Create database models** (Dream, Analysis)
2. **Setup Alembic** for migrations
3. **Create first migration** (creates tables)
4. **Test** - can we create a dream in the DB?

---

## Tech Stack Reminder

**Already Setup** ✅:

- FastAPI (async API)
- PostgreSQL + pgvector (database + vector search)
- Redis (caching)
- Docker Compose (local dev)
- SQLAlchemy 2.0 (async ORM)
- Alembic (migrations)

**To Add**:

- Gradio (UI)
- LangGraph (agent orchestration)
- LiteLLM (unified LLM API)
- OpenAI/Anthropic SDKs (AI models)
- arq (background jobs)

---
