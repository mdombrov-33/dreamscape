from contextlib import asynccontextmanager

import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import engine
from app.db import base  # noqa: F401 - Import models for SQLAlchemy
from app.ui.gradio_app import gradio_ui

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Dreamscape API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(
        f"Database: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    )

    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

    yield

    logger.info("Shutting down Dreamscape API")
    await engine.dispose()
    logger.info("Database connections closed")


app = FastAPI(
    title=settings.app_name,
    description="Dream analysis system with multi-agent AI and evaluation framework",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

app = gr.mount_gradio_app(app, gradio_ui, path="/ui")


@app.get("/health", tags=["health"])
async def health_check():

    return {
        "status": "healthy",
        "environment": settings.environment,
        "app": settings.app_name,
    }
