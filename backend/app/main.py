from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine

from app.models.role import Role  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.weekly_report import WeeklyReport  # noqa: F401
from app.models.ai_summary import AISummary  # noqa: F401
from app.models.activity_log import ActivityLog  # noqa: F401

from app.routers.auth_router import router as auth_router
from app.routers.project_router import router as project_router
from app.routers.report_router import router as report_router
from app.routers.dashboard_router import router as dashboard_router
from app.routers.ai_router import router as ai_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PulseBoard API",
    version="1.0.0",
    description="Role-based weekly reporting and team dashboard API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(project_router, prefix="/api/v1")
app.include_router(report_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "PulseBoard API"}
