# 🌙 Dreamscape

Production-grade dream analysis system with multi-agent AI and comprehensive evaluation framework.

## Overview

Dreamscape combines dream journaling with a sophisticated AI evaluation infrastructure. Multiple agents with different analysis strategies are orchestrated via LangGraph, with LiteLLM providing unified access to various LLM providers. A custom evaluation framework measures and compares agent performance across quality, consistency, and cost metrics.

## Core Features

### Multi-Agent Analysis System

- Multiple AI agents analyze dreams using different models and prompting strategies
- Agent orchestration via LangGraph workflows
- Swappable LLM providers (OpenAI, Anthropic, Ollama) through LiteLLM
- Ensemble approach combines insights from multiple agents
- Prompt caching via LiteLLM for cost optimization

### Evaluation Framework

- **Consistency testing** - Output stability across identical inputs
- **Quality scoring** - LLM-as-judge evaluation of analysis depth
- **Hallucination detection** - Identifies unsupported claims
- **A/B testing** - Systematic prompt variation comparison
- **Regression testing** - Quality monitoring across changes
- **Golden datasets** - Curated test cases with expected outputs

### Metrics & Monitoring

- Symbol detection accuracy
- Emotional tone consistency
- Insight depth scoring
- Response latency tracking
- Cost per analysis (with caching metrics)
- User satisfaction ratings

## Architecture

```
dreamscape/
├── app/
│   ├── agents/              # AI agents for dream analysis
│   │   ├── base_agent.py           # Abstract agent interface
│   │   ├── symbol_agent.py         # Symbol detection
│   │   ├── emotion_agent.py        # Emotional analysis
│   │   ├── insight_agent.py        # Psychological insights
│   │   └── ensemble_agent.py       # Multi-agent orchestration
│   │
│   ├── evals/               # Evaluation framework
│   │   ├── evaluators/             # Evaluation strategies
│   │   │   ├── consistency_eval.py
│   │   │   ├── quality_eval.py
│   │   │   └── hallucination_eval.py
│   │   ├── metrics/                # Metric collectors
│   │   ├── datasets/               # Golden datasets
│   │   └── reporters/              # Results & visualization
│   │
│   ├── api/v1/              # REST API endpoints
│   │   ├── dreams.py               # Dream CRUD
│   │   ├── analysis.py             # Trigger analysis
│   │   └── evals.py                # Run evaluations
│   │
│   ├── services/            # Business logic layer
│   ├── models/              # Pydantic schemas
│   ├── db/                  # Database layer
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── session.py              # Session management
│   │   └── migrations/             # Alembic migrations
│   │
│   └── core/                # Core utilities
│       ├── config.py               # Configuration
│       ├── logging.py              # Structured logging
│       └── deps.py                 # FastAPI dependencies
│
├── tests/                   # Test suite
│   ├── test_agents/
│   ├── test_evals/
│   └── test_api/
│
└── scripts/                 # Utility scripts
    ├── run_evals.py
    └── seed_data.py
```

## Tech Stack

### Core Backend

- **FastAPI** - Async web framework
- **PostgreSQL** - Primary database with pgvector extension
- **SQLAlchemy 2.0** - Async ORM
- **Alembic** - Database migrations
- **Pydantic v2** - Data validation & serialization
- **Redis** - Caching & rate limiting

### AI & Agent Infrastructure

- **LangGraph** - Agent orchestration and workflow management
- **LiteLLM** - Unified API for multiple LLM providers + prompt caching
- **OpenAI API** - GPT-4 for high-quality analysis
- **Anthropic API** - Claude for alternative perspectives
- **Ollama** - Local models (Qwen 2.5)
- **pgvector** - Vector embeddings for semantic search

### Evaluation & Monitoring

- **Custom eval framework** - Built from scratch for dream analysis
- **Loguru** - Structured logging
- **Prometheus** (optional) - Metrics collection
- **arq** - Background task queue for async analysis

### Development & Testing

- **uv** - Fast Python package manager
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **httpx** - Async HTTP client
- **mypy** - Static type checking

## Key Technical Decisions

**Why LangGraph?**

- Production-ready agent orchestration
- State management for multi-step workflows
- Built for agentic patterns (no LangChain baggage)

**Why LiteLLM?**

- Unified API across OpenAI/Anthropic/Ollama
- Built-in prompt caching (reduces costs)
- Fallback & retry logic
- Usage tracking out of the box

**Why Custom Evals?**

- Domain-specific metrics for dream analysis
- Full control over evaluation logic
- Understanding eval patterns from first principles

## Project Goals

- Multi-agent dream analysis system with LangGraph orchestration
- Production-quality evaluation framework for measuring AI output quality
- Systematic comparison of different models and prompting strategies
- Cost optimization through caching and intelligent model selection
- Comprehensive metrics for quality, consistency, and performance
