from fastapi import APIRouter
from app.api.routers import library, document, chunk

router = APIRouter()

@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


router.include_router(library.router)
router.include_router(document.router)
router.include_router(chunk.router)
router.include_router(chunk.search_router)