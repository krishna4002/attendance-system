from passlib.context import CryptContext
from fastapi import HTTPException, Header, Depends

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ADMIN_HEADER_NAME = "x-admin-password"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False

def require_admin(x_admin_password: str = Header(None)):
    """
    This dependency expects the raw admin password in header 'x-admin-password'.
    The router will validate against hashed password stored in DB.
    Use require_admin only for endpoints that want to enforce header presence.
    """
    if not x_admin_password:
        raise HTTPException(status_code=401, detail="Missing admin password header")
    return x_admin_password
