"""
Import all models here so Alembic can discover them.
This file is imported by alembic/env.py
"""

from app.core.database import Base  # noqa: F401
from app.db.models.analysis import Analysis  # noqa: F401
from app.db.models.dream import Dream  # noqa: F401
