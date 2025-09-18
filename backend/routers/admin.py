from fastapi import APIRouter, Depends, HTTPException, Form
from backend.database import get_db
from backend.utils.security import hash_password, verify_password, require_admin
from backend.utils.embeddings import build_embeddings_for, load_embeddings
from pathlib import Path

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent

@router.post("/set-password")
def set_password(password: str = Form(...), db=Depends(get_db)):
    pw_hash = hash_password(password)
    # Either update existing admin row or create one
    if db.execute("SELECT 1 FROM admin WHERE id=1").fetchone():
        db.execute("UPDATE admin SET password_hash = ? WHERE id = 1", (pw_hash,))
    else:
        db.execute("INSERT INTO admin (id, password_hash) VALUES (1, ?)", (pw_hash,))
    db.commit()
    return {"message": "Admin password set"}

@router.post("/check-password")
def check_password(password: str = Form(...), db=Depends(get_db)):
    row = db.execute("SELECT password_hash FROM admin WHERE id=1").fetchone()
    if not row:
        raise HTTPException(404, "Admin password not set")
    if verify_password(password, row[0]):
        return {"valid": True}
    raise HTTPException(401, "Invalid password")

@router.post("/regen-embeddings")
def regen_all(admin_pw: str = Depends(require_admin), db=Depends(get_db)):
    # We require header presence via require_admin; verify value against stored hash
    stored = db.execute("SELECT password_hash FROM admin WHERE id=1").fetchone()
    if not stored:
        raise HTTPException(400, "Admin password not set")
    if not verify_password(admin_pw, stored[0]):
        raise HTTPException(401, "Bad admin password")
    s_count = build_embeddings_for("students")
    t_count = build_embeddings_for("teachers")
    return {"message": f"Embeddings regenerated. Students: {s_count}, Teachers: {t_count}"}

@router.get("/embeddings-info")
def embeddings_info(admin_pw: str = Depends(require_admin), db=Depends(get_db)):
    stored = db.execute("SELECT password_hash FROM admin WHERE id=1").fetchone()
    if not stored or not verify_password(admin_pw, stored[0]):
        raise HTTPException(401, "Bad admin password")
    s = load_embeddings("students")
    t = load_embeddings("teachers")
    return {"students": len(s), "teachers": len(t)}

@router.get("/attendance/all")
def all_attendance(admin_pw: str = Depends(require_admin), db=Depends(get_db)):
    stored = db.execute("SELECT password_hash FROM admin WHERE id=1").fetchone()
    if not stored or not verify_password(admin_pw, stored[0]):
        raise HTTPException(401, "Bad admin password")
    s = db.execute("SELECT * FROM attendance_students").fetchall()
    t = db.execute("SELECT * FROM attendance_teachers").fetchall()
    return {"students": [dict(r) for r in s], "teachers": [dict(r) for r in t]}

@router.delete("/attendance/reset")
def reset_attendance(admin_pw: str = Depends(require_admin), db=Depends(get_db)):
    stored = db.execute("SELECT password_hash FROM admin WHERE id=1").fetchone()
    if not stored or not verify_password(admin_pw, stored[0]):
        raise HTTPException(401, "Bad admin password")
    db.execute("DELETE FROM attendance_students")
    db.execute("DELETE FROM attendance_teachers")
    db.commit()
    return {"message": "Attendance cleared"}
