from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.dream import DreamCreate, DreamRead, DreamUpdate
from app.services.analysis_service import AnalysisService
from app.services.dream_service import DreamService

router = APIRouter()


@router.post("/dreams", response_model=DreamRead, status_code=status.HTTP_201_CREATED)
async def create_dream(
    dream: DreamCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new dream and analyze it with AI.

    - **content**: The dream description (required, 1-10000 chars)
    - **dream_date**: When the dream occurred (optional, defaults to now)

    Returns the dream with AI analysis.
    """
    dream_service = DreamService(db)
    created_dream = await dream_service.create_dream(
        content=dream.content,
        dream_date=dream.dream_date,
    )

    analysis_service = AnalysisService(db)
    await analysis_service.analyze_dream_with_agent(
        dream_id=created_dream.id,
        dream_content=created_dream.content,
    )

    dream_with_analyses = await dream_service.get_dream_with_analyses(created_dream.id)
    return dream_with_analyses


@router.get("/dreams", response_model=list[DreamRead])
async def get_dreams(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all dreams with pagination.

    - **skip**: Number of dreams to skip (default: 0)
    - **limit**: Max dreams to return (default: 100, max: 100)
    """
    service = DreamService(db)
    return await service.get_all_dreams(skip=skip, limit=limit)


@router.get("/dreams/{dream_id}", response_model=DreamRead)
async def get_dream(
    dream_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single dream by ID.

    - **dream_id**: The ID of the dream to retrieve
    """
    service = DreamService(db)
    dream = await service.get_dream_by_id(dream_id)

    if not dream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dream with id {dream_id} not found",
        )

    return dream


@router.put("/dreams/{dream_id}", response_model=DreamRead)
async def update_dream(
    dream_id: int,
    dream_update: DreamUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a dream.

    - **dream_id**: The ID of the dream to update
    - **content**: New dream content (optional)
    - **dream_date**: New dream date (optional)
    """
    service = DreamService(db)
    updated_dream = await service.update_dream(
        dream_id=dream_id,
        content=dream_update.content,
        dream_date=dream_update.dream_date,
    )

    if not updated_dream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dream with id {dream_id} not found",
        )

    return updated_dream


@router.delete("/dreams/{dream_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dream(
    dream_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a dream.

    - **dream_id**: The ID of the dream to delete
    """
    service = DreamService(db)
    success = await service.delete_dream(dream_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dream with id {dream_id} not found",
        )

    return None  # 204 returns no content
