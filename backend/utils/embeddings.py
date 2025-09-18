from pathlib import Path
import numpy as np
import face_recognition

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
EMB_DIR = BASE_DIR / "embeddings"
EMB_DIR.mkdir(parents=True, exist_ok=True)

def _role_dir(role: str) -> Path:
    # role is 'students' or 'teachers'
    return DATASET_DIR / role

def build_embeddings_for(role: str) -> int:
    """
    role => 'students' or 'teachers'
    Scans dataset/<role>/* and creates a dict:
       { id: {"name": name, "embedding": ndarray} }
    Saves to embeddings/student_embeddings.npy or teacher_embeddings.npy
    Returns number of identities processed.
    """
    base = _role_dir(role)
    enc_map = {}
    if not base.exists():
        return 0
    for person in base.iterdir():
        if not person.is_dir():
            continue
        parts = person.name.split("_")
        if len(parts) < 2:
            continue
        pid = parts[0]
        name = "_".join(parts[1:])
        encs = []
        for img_path in person.glob("*.*"):
            try:
                img = face_recognition.load_image_file(str(img_path))
                locs = face_recognition.face_locations(img)
                if not locs:
                    continue
                encs.extend(face_recognition.face_encodings(img, locs))
            except Exception:
                continue
        if encs:
            enc_map[pid] = {"name": name, "embedding": np.mean(encs, axis=0)}
    save_file = EMB_DIR / f"{role[:-1]}_embeddings.npy"  # student_embeddings.npy
    np.save(save_file, enc_map)
    return len(enc_map)

def load_embeddings(role: str) -> dict:
    f = EMB_DIR / f"{role[:-1]}_embeddings.npy"
    if not f.exists():
        return {}
    return np.load(f, allow_pickle=True).item()

def match_embedding(face_encoding, role: str, threshold: float = 0.6):
    """
    face_encoding: numpy array
    role: 'students' or 'teachers'
    returns tuple (id, name, distance) if matched else None
    """
    data = load_embeddings(role)
    if not data:
        return None
    best = None
    best_d = 1e9
    for pid, rec in data.items():
        d = float(np.linalg.norm(face_encoding - rec["embedding"]))
        if d < best_d:
            best_d = d
            best = (pid, rec["name"], d)
    if best and best[2] <= threshold:
        return best
    return None
