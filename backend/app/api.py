from fastapi import APIRouter
from app.routers import ai_router, auth_router, dashboard_router, project_router, report_router, user_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router.router)
api_router.include_router(user_router.router)
api_router.include_router(project_router.router)
api_router.include_router(report_router.router)
api_router.include_router(dashboard_router.router)
api_router.include_router(ai_router.router)
