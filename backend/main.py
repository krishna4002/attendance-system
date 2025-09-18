from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.routers import students, teachers, attendance, admin, schedules
from backend.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="School Attendance System")


# --- API routes first ---
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["Teachers"])
app.include_router(attendance.router, prefix="/api", tags=["Attendance"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["Schedules"])

@app.get("/api/health")
def health():
    return {"status": "ok"}

# --- Mount static frontend last ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
