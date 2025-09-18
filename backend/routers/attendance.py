from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from pathlib import Path
from io import BytesIO
import face_recognition
from backend.utils.embeddings import match_embedding
from backend.database import get_db
import datetime

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent

@router.post("/recognize/student")
async def recognize_student(file: UploadFile = File(...), db=Depends(get_db)):
    img_bytes = await file.read()
    try:
        img = face_recognition.load_image_file(BytesIO(img_bytes))
    except Exception:
        raise HTTPException(400, "Invalid image")
    locs = face_recognition.face_locations(img)
    if not locs:
        raise HTTPException(404, "Face not found")
    enc = face_recognition.face_encodings(img, locs)[0]
    matched = match_embedding(enc, "students")
    if not matched:
        raise HTTPException(404, "No match")
    sid, name, dist = matched
    now = datetime.datetime.now()
    db.execute(
        "INSERT INTO attendance_students (student_id, date, time, status) VALUES (?, ?, ?, ?)",
        (sid, now.date().isoformat(), now.time().strftime("%H:%M:%S"), "Present")
    )
    db.commit()
    return {"message": f"Attendance marked for {name} (ID: {sid})", "distance": dist}

@router.post("/recognize/teacher")
async def recognize_teacher(file: UploadFile = File(...), db=Depends(get_db)):
    img_bytes = await file.read()
    try:
        img = face_recognition.load_image_file(BytesIO(img_bytes))
    except Exception:
        raise HTTPException(400, "Invalid image")
    locs = face_recognition.face_locations(img)
    if not locs:
        raise HTTPException(404, "Face not found")
    enc = face_recognition.face_encodings(img, locs)[0]
    matched = match_embedding(enc, "teachers")
    if not matched:
        raise HTTPException(404, "No match")
    tid, name, dist = matched
    now = datetime.datetime.now()
    db.execute(
        "INSERT INTO attendance_teachers (teacher_id, date, time, status) VALUES (?, ?, ?, ?)",
        (tid, now.date().isoformat(), now.time().strftime("%H:%M:%S"), "Present")
    )
    db.commit()
    return {"message": f"Attendance marked for {name} (ID: {tid})", "distance": dist}
