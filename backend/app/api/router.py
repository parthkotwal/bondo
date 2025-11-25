from fastapi import APIRouter
from app.api.run import router as run_router
from app.api.docs import router as docs_router
from app.api.mentor import router as mentor_router

router = APIRouter()

router.include_router(run_router)
router.include_router(docs_router)
router.include_router(mentor_router)
