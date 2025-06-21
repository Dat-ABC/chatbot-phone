from fastapi import APIRouter
from .chat import router as api_router

router = APIRouter()
router.include_router(api_router, prefix="/chat", tags=["chat"]) 