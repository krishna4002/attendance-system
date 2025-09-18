from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import StudentCreate
from pathlib import Path
from backend.utils.embeddings import build_embeddings_for
import shutil
import os

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
DATASET_DIR.mkdir(parents=True, exist_ok=True)
(DATASET_DIR / "students").mkdir(parents=True, exist_ok=True)

@router.post("/register")
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    # check exists
    row = db.execute("SELECT 1 FROM students WHERE student_id = :id", {"id": data.student_id}).fetchone()
    if row:
        raise HTTPException(400, "Student ID already exists")
    db.execute("INSERT INTO students (student_id, name) VALUES (:id, :name)", {"id": data.student_id, "name": data.name})
    db.commit()
    folder = DATASET_DIR / "students" / f"{data.student_id}_{data.name.replace(' ', '_')}"
    folder.mkdir(parents=True, exist_ok=True)
    # Note: embeddings will be regenerated after images upload or you may call build_embeddings_for('students')
    return {"message": "Student registered", "folder": str(folder)}

@router.post("/register/upload-images")
async def upload_student_images(student_id: str = Form(...), files: list[UploadFile] = File(...)):
    base = DATASET_DIR / "students"
    target = None
    for d in base.glob(f"{student_id}_*"):
        if d.is_dir():
            target = d
            break
    if not target:
        raise HTTPException(400, "Student folder not found; register first")
    saved = 0
    for f in files:
        contents = await f.read()
        out_path = target / f.filename
        out_path.write_bytes(contents)
        saved += 1
    # regenerate embeddings automatically
    count = build_embeddings_for("students")
    return {"message": f"Saved {saved} files; embeddings updated (total identities: {count})"}

@router.get("/list")
def list_students(db: Session = Depends(get_db)):
    rows = db.execute("SELECT student_id, name FROM students").fetchall()
    return {"students": [{"student_id": r[0], "name": r[1]} for r in rows]}

@router.delete("/{student_id}")
def delete_student(student_id: str, db: Session = Depends(get_db)):
    # remove DB entry
    db.execute("DELETE FROM students WHERE student_id = :id", {"id": student_id})
    db.commit()
    # remove dataset folder if present
    base = DATASET_DIR / "students"
    for d in base.glob(f"{student_id}_*"):
        if d.is_dir():
            # delete directory tree
            shutil.rmtree(d)
    # regenerate embeddings
    build_embeddings_for("students")
    return {"message": "Student removed"}
