from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from backend.database import get_db
import csv
from io import StringIO

router = APIRouter()

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), db=Depends(get_db)):
    content = (await file.read()).decode('utf-8')
    reader = csv.DictReader(StringIO(content))
    count = 0
    for row in reader:
        # expected columns: class_id,subject,teacher_id,day,start_time,end_time
        db.execute("INSERT INTO schedules (class_id, subject, teacher_id, day, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?)",
                   (row.get('class_id'), row.get('subject'), row.get('teacher_id'), row.get('day'), row.get('start_time'), row.get('end_time')))
        count += 1
    db.commit()
    return {"message": f"Uploaded {count} schedule rows"}

@router.get("/list")
def list_schedules(db=Depends(get_db)):
    rows = db.execute("SELECT * FROM schedules").fetchall()
    return {"schedules": [dict(r) for r in rows]}
