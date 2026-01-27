from fastapi import APIRouter
from app.api.auth.routes import router as authRoutes

router = APIRouter(prefix='/api/auth', tags=['auth'])

router.include_router(authRoutes)
