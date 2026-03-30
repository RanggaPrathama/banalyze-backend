from app.modules.auth import auth_router
from app.modules.user import user_router
from app.modules.history_classify import history_classify_router
from fastapi import APIRouter

router = APIRouter(prefix="/api")

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(user_router, prefix="/user", tags=["User"])
router.include_router(history_classify_router, prefix="/history-classify", tags=["History Classify"])
