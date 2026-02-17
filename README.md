# 🌙 Dreamscape

> **Multi-agent AI platform** for dream analysis — compare models, track quality, explore orchestration patterns

## What Is This?

Dreamscape runs your dream through a pipeline of specialized AI agents and lets you swap the model powering each one. The goal is to see what actually produces useful analysis and at what cost.

- Submit a dream → **Generalist** maps the landscape (symbols, emotions, themes)
- **Specialists** go deep on each area in parallel
- **Synthesizer** combines everything into a final interpretation
- Any agent can run any model — local Qwen or cloud (GPT-5, Claude, Gemini)

## How It Works

```
Dream input
    ↓
Generalist        — broad first-pass (symbols, emotions, themes, overview)
    ↓
Symbol Specialist ─┐
Emotion Specialist ─┼─ run in parallel, each gets generalist output as context
Theme Specialist  ─┘
    ↓
Synthesizer       — combines all specialist analyses into final interpretation
```

Each agent's output and the model used are stored in the database.

## Current Features

- ✅ Dream journal with AI analysis
- ✅ Streaming responses
- ✅ Gradio web UI with model dropdown
- ✅ Local LLM support (Ollama/Qwen)
- ✅ Cloud models via OpenRouter (GPT-5, Claude, Gemini)
- ✅ Tracks agent type and model used per analysis

## Coming Soon

- 🔄 Multi-agent LangGraph workflow (specialists + synthesizer)
- 🔄 Side-by-side analysis display per agent
- 🔄 Rating system
- 🔄 Cost and quality dashboard

## Tech Stack

- **FastAPI** — API
- **SQLAlchemy + PostgreSQL** — database
- **Gradio** — web UI (mounted at `/ui`)
- **LiteLLM** — unified interface for Ollama, OpenAI, Anthropic, OpenRouter
- **LangGraph** — agent orchestration

## Quick Start

```bash
# Copy and fill in your OpenRouter key (optional, Qwen works locally for free)
cp .env.example .env

# Start
docker-compose up -d

# UI
open http://localhost:8000/ui

# API docs
open http://localhost:8000/docs
```

---

**Status:** Phase 1 complete, Phase 2 in progress — see `docs/roadmap.md`
