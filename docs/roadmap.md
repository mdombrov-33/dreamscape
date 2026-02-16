# Dreamscape Development Roadmap

## Vision

**An AI evaluation platform that answers: "Which AI approach works best for dream interpretation?"**

Test different models (GPT-4o, Claude, Qwen), prompt strategies (Jungian, Freudian, cognitive), and orchestration patterns (single vs multi-agent) to determine optimal configurations for quality and cost.

## Core User Flow

```
1. User enters dream
2. Select AI configuration (preset or custom models per agent)
3. LangGraph orchestrates multi-agent workflow:
   - Generalist extracts structure (symbols, emotions, themes)
   - Specialists deep-dive in parallel
   - Synthesizer combines into final interpretation
4. User sees all analyses side-by-side
5. User rates which was most helpful
6. System learns optimal configurations
```

---

## Phase 1: MVP ✅ COMPLETE

**Goal:** Basic dream journal with single AI agent

### 1.1 Infrastructure ✅
- [x] Docker Compose setup (PostgreSQL + Redis)
- [x] FastAPI application structure
- [x] Alembic migrations
- [x] Database models (Dream, Analysis)

### 1.2 Basic API ✅
- [x] POST /dreams - Create dream
- [x] GET /dreams - List dreams
- [x] GET /dreams/{id} - Get dream with analyses
- [x] Pydantic schemas

### 1.3 First AI Agent ✅
- [x] Ollama client (local LLM)
- [x] BaseAgent interface
- [x] SimpleDreamAnalyzer
- [x] Streaming support
- [x] Analysis service

### 1.4 Gradio UI ✅
- [x] Dream input form
- [x] Streaming analysis display
- [x] Past dreams table
- [x] Mounted at /ui

---

## Phase 2: Multi-Agent LangGraph Workflow 🔄 IN PROGRESS

**Goal:** Sequential agent orchestration with model swapping

### 2.1 LiteLLM Integration (Next - 1 hour)
```bash
Files to create:
- app/core/litellm_client.py
- Update agents to use LiteLLM
```

**What:**
- [x] Add database fields (agent_type, model_used)
- [ ] Install LiteLLM
- [ ] Create unified client (Ollama, OpenAI, Anthropic, OpenRouter)
- [ ] Config for API keys
- [ ] Test: Qwen vs GPT-4o-mini vs Claude Haiku

**Why:** Foundation for model swapping and cost tracking

---

### 2.2 Generalist Agent (1 hour)
```bash
Files to create:
- app/agents/generalist_agent.py
```

**What:**
- [ ] Create GeneralistAgent
- [ ] Extracts structured data:
  ```python
  {
    "symbols": ["flying", "forest", "shadows"],
    "emotions": ["anxiety", "freedom", "fear"],
    "themes": ["escape", "pursuit", "unknown"],
    "key_phrases": ["whispered my name"]
  }
  ```
- [ ] Outputs both structured + prose analysis

**Prompt:** "Extract symbols, emotions, and themes from this dream. Be comprehensive but structured."

---

### 2.3 Specialist Agents (2 hours)
```bash
Files to create:
- app/agents/symbol_specialist.py
- app/agents/emotion_specialist.py
- app/agents/theme_specialist.py
```

**What:**
- [ ] **SymbolSpecialist:** Deep dive on each symbol
  - Input: Original dream + generalist's symbol list
  - Output: Detailed meaning of each symbol

- [ ] **EmotionSpecialist:** Emotional analysis
  - Input: Original dream + generalist's emotion list
  - Output: Emotional scores, conflicts, arcs

- [ ] **ThemeSpecialist:** Thematic interpretation
  - Input: Original dream + generalist's theme list
  - Output: Deep exploration of themes

---

### 2.4 Synthesizer Agent (1 hour)
```bash
Files to create:
- app/agents/synthesizer_agent.py
```

**What:**
- [ ] Combines all specialist analyses
- [ ] Creates unified interpretation
- [ ] Highlights key insights
- [ ] Input: All previous analyses
- [ ] Output: Final comprehensive interpretation

---

### 2.5 LangGraph Workflow (2 hours)
```bash
Files to create:
- app/workflows/dream_analysis.py
```

**What:**
- [ ] Install LangGraph
- [ ] Define workflow:
  ```python
  Dream → Generalist → [Symbol, Emotion, Theme] (parallel) → Synthesizer
  ```
- [ ] State management
- [ ] Error handling
- [ ] Progress tracking

---

### 2.6 Updated UI (3 hours)
```bash
Files to update:
- app/ui/gradio_app.py
```

**What:**
- [ ] Model selection dropdowns (before entering dream)
  ```
  Generalist: [Qwen | GPT-4o-mini | Claude Haiku]
  Symbol: [Qwen | GPT-4o-mini | Claude Haiku]
  Emotion: [Qwen | GPT-4o-mini | Claude Haiku]
  Theme: [Qwen | GPT-4o-mini | Claude Haiku]
  Synthesizer: [Qwen | GPT-4o-mini | Claude Haiku]

  Or: [Preset: All Qwen (Free) ▼]
  ```

- [ ] Side-by-side analysis display:
  ```
  ┌─────────────┬─────────────┬─────────────┐
  │ Symbol      │ Emotion     │ Theme       │
  │ Analysis    │ Analysis    │ Analysis    │
  └─────────────┴─────────────┴─────────────┘

  ┌─────────────────────────────────────────┐
  │ Final Synthesis                         │
  └─────────────────────────────────────────┘
  ```

- [ ] Progress indicator (which agent is working)
- [ ] Cost estimate display

---

## Phase 3: Evaluation Framework (5-7 hours)

**Goal:** Track which configurations work best

### 3.1 Rating System (2 hours)
- [ ] Add rating UI (5 stars per analysis)
- [ ] Store ratings in database:
  ```python
  AnalysisRating:
    - analysis_id
    - rating (1-5)
    - feedback_text (optional)
  ```
- [ ] Overall helpfulness rating

### 3.2 Cost Tracking (1 hour)
- [ ] Track tokens used per analysis
- [ ] Calculate cost per configuration
- [ ] Display cost in UI

### 3.3 Analytics Dashboard (2 hours)
- [ ] New Gradio tab: "📊 Analytics"
- [ ] Show:
  - Avg rating per agent type
  - Avg rating per model
  - Cost vs quality chart
  - Most popular configurations
  - Win rate per agent

### 3.4 A/B Testing (2 hours)
- [ ] Random configuration assignment
- [ ] Statistical significance tests
- [ ] Recommendation engine: "Use GPT-4o for synthesis, Qwen for extraction"

---

## Phase 4: Advanced Features (Optional)

### 4.1 Embeddings & Semantic Search
- [ ] Generate embeddings for dreams
- [ ] Store in pgvector
- [ ] "Find similar dreams" feature

### 4.2 Pattern Tracking (Requires Auth)
- [ ] Simple authentication
- [ ] Track symbols across YOUR dreams
- [ ] "Flying appears in 40% of your dreams"
- [ ] Emotional trends over time

### 4.3 Custom Prompts
- [ ] UI for editing agent prompts
- [ ] Save custom configurations
- [ ] Share configurations

### 4.4 Batch Analysis
- [ ] Analyze multiple dreams
- [ ] Export to CSV/JSON
- [ ] Bulk evaluation

---

## Technical Decisions

### Why This Order?

1. **LiteLLM first** → Foundation for everything
2. **Agents next** → Core functionality
3. **LangGraph** → Orchestration
4. **UI** → Make it usable
5. **Evaluation** → Learn from data

### Models to Support

**Free (Ollama):**
- Qwen 2.5:7b (current)
- Llama 3.2
- Mistral

**Paid (via LiteLLM):**
- **OpenAI:** GPT-4o ($2.50/1M in, $10/1M out), GPT-4o-mini ($0.15/1M in, $0.60/1M out)
- **Anthropic:** Claude 3.5 Sonnet ($3/1M in, $15/1M out), Claude 3.5 Haiku ($0.25/1M in, $1.25/1M out)
- **OpenRouter:** Access to 100+ models with unified billing

### Prompt Strategies

1. **General:** Balanced interpretation
2. **Jungian:** Archetypes, collective unconscious
3. **Freudian:** Unconscious desires, symbolism
4. **Cognitive:** Problem-solving, memory processing
5. **Gestalt:** Present experience, awareness

---

## Success Metrics

**Phase 2 Success:**
- Multi-agent workflow running
- Model swapping working
- UI showing all analyses

**Phase 3 Success:**
- 100+ rated dream analyses
- Clear winner: "GPT-4o Jungian gets 4.5/5 avg"
- Cost analysis: "Optimal config: $0.01/dream, 4.2/5 rating"

**Overall Success:**
- Answered: "Which AI is best for dreams?"
- Built evaluation framework
- Learned LangGraph + LiteLLM
- Had fun with AI! 🌙

---

## Current Status

**Completed:**
- ✅ Phase 1 (MVP with single agent)

**In Progress:**
- 🔄 Phase 2.1 (LiteLLM integration)

**Next Up:**
- Generalist agent
- Specialist agents
- LangGraph workflow
- Updated UI

**Timeline:** Phase 2 = ~10 hours of focused work
