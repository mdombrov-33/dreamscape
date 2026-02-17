# 🌙 Dreamscape

> **Collective dream analysis** — multi-agent pipeline that analyzes dreams, extracts structured tags and embeddings, and surfaces patterns across a shared dream atlas

## What Is This?

Dreamscape runs a dream through a multi-agent pipeline. Each agent has a specific role. Outputs stream live into the UI as they arrive. Every analysis is stored with tags and embeddings — over time the system builds a collective knowledge base: common symbols, recurring themes, semantically similar dreams.

No auth. All dreams are anonymous and shared. You contribute to a growing pool; you can also search it.

## Agent Pipeline

```
Generalist          — maps the dream: symbols, emotions, themes, overview  [streams live]
    ↓
Symbol Specialist ──┐
Emotion Specialist ─┼── parallel, stream into their panels simultaneously  [streams live]
Theme Specialist  ──┘
    ↓
Rating Agent        — LLM-as-a-judge scores each specialist (1-5, informational)
    ↓
Synthesizer         — combines everything into a final interpretation       [streams live]
```

All outputs stored in DB: agent name, model used, content, score.

## The Collective Layer (coming)

After analysis, a lightweight step extracts:
- **Tags** — 3–5 tokens per dream (`water`, `falling`, `anxiety`, `transformation`)
- **Embeddings** — vector of the full analysis, stored in pgvector

This enables:
- **Similar dreams** — semantic search on what you just analyzed
- **Explore tab** — tag clouds, common symbols, theme frequency across all dreams
- **Dream clusters** — "47 dreams about pursuit and anxiety; here's the pattern"

## Current Features

- ✅ Dream journal with AI analysis
- ✅ Live parallel streaming (all three specialists stream simultaneously)
- ✅ Gradio web UI with model dropdown
- ✅ Local LLM support (Ollama/Qwen)
- ✅ Cloud models via OpenRouter (GPT-5, Claude, Gemini)
- ✅ LLM-as-a-judge scoring (informational, shown per panel)

## Coming Soon

- 🔄 Tag extraction agent (structured JSON output)
- 🔄 Embeddings + pgvector similarity search
- 🔄 Explore tab — collective patterns across all dreams
- 🔄 Manual retry button for low-scored analyses
- 🔄 Cost tracking (tokens in/out per analysis)

## Tech Stack

- **FastAPI** — API
- **SQLAlchemy + PostgreSQL + pgvector** — database with vector search
- **Gradio** — web UI (mounted at `/ui`)
- **LiteLLM** — unified interface for Ollama, OpenAI, Anthropic, OpenRouter
- **LangGraph** — agent orchestration

## Quick Start

```bash
cp .env.example .env          # add OPENROUTER_API_KEY (optional, Qwen is free)
docker-compose up -d
open http://localhost:8000/ui
```

---

**Status:** Phase 2 complete (streaming pipeline), Phase 3 next — see `docs/roadmap.md`
