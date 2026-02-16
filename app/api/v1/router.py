from fastapi import APIRouter

api_router = APIRouter()

# As we build features, we'll add routers like this:
# from app.api.v1 import dreams, analysis, evals
# api_router.include_router(dreams.router, prefix="/dreams", tags=["dreams"])
# api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
# api_router.include_router(evals.router, prefix="/evals", tags=["evals"])
