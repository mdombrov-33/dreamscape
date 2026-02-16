from fastapi import APIRouter

from app.api.v1 import dreams

api_router = APIRouter()

api_router.include_router(dreams.router, tags=["dreams"])

# As we build more features, we'll add more routers:
# from app.api.v1 import analysis, evals
# api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
# api_router.include_router(evals.router, prefix="/evals", tags=["evals"])
