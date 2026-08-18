from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import get_db
from models import User, Profile
from schemas import RegisterRequest, LoginRequest
from auth import hash_password, verify_password, generate_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    phone = payload.phone.strip() if payload.phone else None
    if phone and db.query(User).filter(User.phone == phone).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")

    user = User(
        name=payload.name, email=payload.email, phone=phone,
        password_hash=hash_password(payload.password),
        token=generate_token(), language_pref=payload.language_pref or "en",
    )
    try:
        db.add(user)
        db.flush()
        db.add(Profile(user_id=user.id))
        db.commit()
        db.refresh(user)
    except IntegrityError:
        # A second concurrent request may pass the checks above; never expose
        # a database exception to the browser in that case.
        db.rollback()
        raise HTTPException(status_code=400, detail="Email or phone number already registered")

    response.set_cookie("csn_token", user.token, httponly=True, max_age=60 * 60 * 24 * 30, samesite="lax")
    return {"message": "Registered successfully", "user": {"id": user.id, "name": user.name, "email": user.email}}


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user.token = generate_token()
    db.commit()

    response.set_cookie("csn_token", user.token, httponly=True, max_age=60 * 60 * 24 * 30, samesite="lax")
    return {"message": "Login successful", "user": {"id": user.id, "name": user.name, "email": user.email}}


@router.post("/logout")
def logout(response: Response, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.token = None
    db.commit()
    response.delete_cookie("csn_token")
    return {"message": "Logged out"}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id, "name": user.name, "email": user.email, "phone": user.phone,
        "language_pref": user.language_pref, "dark_mode": user.dark_mode,
        "digilocker_connected": user.digilocker_connected,
    }
