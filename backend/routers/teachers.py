from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import TeacherCreate
from pathlib import Path
from backend.utils.embeddings import build_embeddings_for

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
DATASET_DIR.mkdir(parents=True, exist_ok=True)
(DATASET_DIR / "teachers").mkdir(parents=True, exist_ok=True)

@router.post("/register")
def create_teacher(data: TeacherCreate, db: Session = Depends(get_db)):
    row = db.execute("SELECT 1 FROM teachers WHERE teacher_id = :id", {"id": data.teacher_id}).fetchone()
    if row:
        raise HTTPException(400, "Teacher ID already exists")
    db.execute("INSERT INTO teachers (teacher_id, name) VALUES (:id, :name)", {"id": data.teacher_id, "name": data.name})
    db.commit()
    folder = DATASET_DIR / "teachers" / f"{data.teacher_id}_{data.name.replace(' ', '_')}"
    folder.mkdir(parents=True, exist_ok=True)
    return {"message": "Teacher registered", "folder": str(folder)}

@router.post("/register/upload-images")
async def upload_teacher_images(teacher_id: str = Form(...), files: list[UploadFile] = File(...)):
    base = DATASET_DIR / "teachers"
    target = None
    for d in base.glob(f"{teacher_id}_*"):
        if d.is_dir():
            target = d
            break
    if not target:
        raise HTTPException(400, "Teacher folder not found; register first")
    saved = 0
    for f in files:
        contents = await f.read()
        out_path = target / f.filename
        out_path.write_bytes(contents)
        saved += 1
    count = build_embeddings_for("teachers")
    return {"message": f"Saved {saved} files; embeddings updated (total identities: {count})"}

@router.get("/list")
def list_teachers(db: Session = Depends(get_db)):
    rows = db.execute("SELECT teacher_id, name FROM teachers").fetchall()
    return {"teachers": [{"teacher_id": r[0], "name": r[1]} for r in rows]}

@router.delete("/{teacher_id}")
def delete_teacher(teacher_id: str, db: Session = Depends(get_db)):
    db.execute("DELETE FROM teachers WHERE teacher_id = :id", {"id": teacher_id})
    db.commit()
    base = DATASET_DIR / "teachers"
    for d in base.glob(f"{teacher_id}_*"):
        if d.is_dir():
            import shutil
            shutil.rmtree(d)
    build_embeddings_for("teachers")
    return {"message": "Teacher removed"}
