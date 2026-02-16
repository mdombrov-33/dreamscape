# 🌙 Dreamscape

> **AI Evaluation Platform** for testing different AI models and approaches on dream analysis

## What Is This?

Dreamscape is an **ML evaluation platform** that answers: **"Which AI approach works best for interpreting dreams?"**

- Test **different models** (Qwen, GPT-4o, Claude) against each other
- Compare **different prompt strategies** (Jungian, Freudian, cognitive)
- Evaluate **orchestration patterns** (single agent vs multi-agent workflows)
- Track **quality vs cost** tradeoffs

Dreams are the perfect test case: subjective, creative, and open to interpretation.

## How It Works

```
1. User enters dream
2. LangGraph orchestrates multi-agent workflow:
   - Generalist extracts symbols, emotions, themes
   - Specialists provide deep analysis (parallel)
   - Synthesizer combines insights
3. Each agent can use different AI models
4. User rates which analysis was most helpful
5. System learns: "GPT-4o Jungian interpretation wins 80% of the time"
```

## Current Features

- ✅ Dream journal with AI analysis
- ✅ Streaming responses (watch AI think in real-time)
- ✅ Gradio web UI
- ✅ Local LLM support (Ollama)

## Coming Soon

- 🔄 Multi-agent LangGraph workflow
- 🔄 Model swapping (GPT-4o, Claude, Qwen)
- 🔄 Rating system
- 🔄 Evaluation dashboard

## Tech Stack

- **FastAPI** - API framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** (pgvector) - Database with vector support
- **Gradio** - Web UI
- **Ollama** - Local LLM inference
- **LiteLLM** - Unified API for multiple AI providers (coming)
- **LangGraph** - Agent orchestration (coming)

## Quick Start

```bash
# Start services
docker-compose up -d

# Open UI
http://localhost:8000/ui

# API docs
http://localhost:8000/docs
```

## Project Goals

1. **Research:** Which AI models are best at dream interpretation?
2. **Evaluation:** Build framework for comparing AI approaches
3. **Learning:** Explore multi-agent systems and LangGraph
4. **Fun:** It's dreams, why not? 🌙

---

**Status:** Early development • Phase 1 complete, Phase 2 in progress

See `docs/roadmap.md` for full development plan.
