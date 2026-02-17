# 🌙 Dreamscape

> **Multi-agent AI evaluation platform** — run dream analysis through a pipeline of specialized agents, auto-score each output with LLM-as-a-judge, and learn which models perform best

## What Is This?

Dreamscape runs a dream through a multi-agent pipeline. Each agent has a specific role. After specialists finish, a rating agent (LLM-as-a-judge) scores each output automatically. Weak analyses get retried with a stronger model. Over time the system builds a dataset: which models consistently produce better analysis at which roles.

## Agent Pipeline

The entire pipeline is a single LangGraph graph. Each agent is a node. State flows through the graph and conditional edges handle retries automatically.

```
Generalist          — maps the dream: symbols, emotions, themes, overview
    ↓
Symbol Specialist ──┐
Emotion Specialist ─┼── parallel nodes, get generalist output as context
Theme Specialist  ──┘
    ↓
Rating Agent        — LLM-as-a-judge scores each specialist (1-5)
    ↓
score < 3 → retry that specialist with escalation model → re-rate
score ≥ 3 → pass to synthesizer
    ↓
Synthesizer         — receives best version of each, writes final interpretation
```

UI shows each node completing in real time with scores and retry indicators.

All outputs stored in DB: agent name, agent type, model used, content, score.

## Why LLM-as-a-Judge?

Writing rules to measure quality of subjective text is hard. Instead, a separate LLM evaluates each analysis on depth, relevance, and insight. This runs automatically — no manual rating needed. Over time you get real data: "Qwen emotion analysis gets escalated 60% of the time" or "Claude Haiku symbol analysis averages 4.2/5."

## Model Escalation

Each model has a fallback if its output scores below threshold:

```
Qwen (local, free) → GPT-5 Nano → Claude Haiku → Claude Sonnet
```

Only the weak analyses get retried. Both versions are saved to DB for comparison.

## Current Features

- ✅ Dream journal with AI analysis
- ✅ Streaming responses
- ✅ Gradio web UI with model dropdown
- ✅ Local LLM support (Ollama/Qwen)
- ✅ Cloud models via OpenRouter (GPT-5, Claude, Gemini)
- ✅ Tracks agent type and model used per analysis

## Coming Soon

- 🔄 Specialist agents (Symbol, Emotion, Theme)
- 🔄 Synthesizer agent
- 🔄 LangGraph workflow with rating agent and conditional retry
- 🔄 Analytics dashboard — scores per model, escalation rates, cost

## Tech Stack

- **FastAPI** — API
- **SQLAlchemy + PostgreSQL** — database
- **Gradio** — web UI (mounted at `/ui`)
- **LiteLLM** — unified interface for Ollama, OpenAI, Anthropic, OpenRouter
- **LangGraph** — agent orchestration with conditional routing

## Quick Start

```bash
cp .env.example .env          # add OPENROUTER_API_KEY (optional, Qwen is free)
docker-compose up -d
open http://localhost:8000/ui
```

---

**Status:** Phase 1 complete, Phase 2 in progress — see `docs/roadmap.md`
