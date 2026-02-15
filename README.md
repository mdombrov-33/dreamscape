# 🌙 Dreamscape

AI-powered dream journal with pattern analysis and
psychological insights.

## What is this?

Track your dreams, discover patterns, and get AI-generated
insights about your subconscious mind.

## Features (planned)

- 📝 Log dreams with details (date, emotions, symbols,
  themes)
- 🤖 AI analysis of dream content (recurring symbols,
  emotional patterns)
- 📊 Pattern detection over time (what triggers certain
  dreams?)
- 🔍 Search dreams by content, emotions, or symbols
- 📈 Visualize dream trends and insights

## Tech Stack

- **FastAPI** - Modern async API framework
- **PostgreSQL** - Main database
- **SQLAlchemy 2.0** - ORM with async support
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **OpenAI/Anthropic API** - Dream analysis and insights
- **uv** - Fast Python package manager

## Architecture

app/
├── api/v1/ # API routes
├── services/ # Business logic + AI integration
├── models/ # Pydantic schemas
├── db/ # SQLAlchemy models + session management
└── core/ # Config, logging, dependencies

## Goal

Learn production-ready Python project structure with real AI
integration.
