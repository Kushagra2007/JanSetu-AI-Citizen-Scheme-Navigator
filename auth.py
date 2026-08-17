import hashlib
import secrets
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User

STATIC_SALT = "csn_static_salt_v1_change_in_prod"


def hash_password(password: str) -> str:
    return hashlib.sha256((STATIC_SALT + password).encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def generate_token() -> str:
    return secrets.token_hex(32)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("csn_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return user


def get_optional_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("csn_token")
    if not token:
        return None
    return db.query(User).filter(User.token == token).first()