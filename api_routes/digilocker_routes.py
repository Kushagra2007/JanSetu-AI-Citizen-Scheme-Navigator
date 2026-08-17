import os
import secrets
from datetime import datetime
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User, Document
from auth import get_current_user

router = APIRouter(prefix="/api/digilocker", tags=["digilocker"])

CLIENT_ID = os.getenv("DIGILOCKER_CLIENT_ID", "mock-client-id")
REDIRECT_URI = os.getenv("DIGILOCKER_REDIRECT_URI", "http://localhost:8000/api/digilocker/callback")

# In-memory mock state store (fine for prototype)
_STATE_STORE = {}

MOCK_DOCS = ["aadhaar", "pan", "driving_license", "voter_id", "passport"]


@router.get("/connect")
def connect(user: User = Depends(get_current_user)):
    state = secrets.token_hex(8)
    _STATE_STORE[state] = user.id
    # Real DigiLocker: redirect to https://digilocker.meripehchaan.gov.in/public/oauth2/1/authorize
    auth_url = (
        f"/api/digilocker/callback?state={state}&code=mockauthcode"
    )
    return {"auth_url": auth_url, "message": "Redirecting to DigiLocker (mock OAuth flow for prototype)"}


@router.get("/callback")
def callback(state: str, code: str, db: Session = Depends(get_db)):
    user_id = _STATE_STORE.pop(state, None)
    if not user_id:
        return RedirectResponse(url="/settings?digilocker=error")

    user = db.query(User).filter(User.id == user_id).first()
    user.digilocker_connected = True
    db.commit()

    for doc_type in MOCK_DOCS:
        doc = db.query(Document).filter(Document.user_id == user_id, Document.doc_type == doc_type).first()
        if not doc:
            doc = Document(user_id=user_id, doc_type=doc_type)
            db.add(doc)
        doc.has_document = True
        doc.verified = True
        doc.source = "digilocker"
        doc.doc_number = f"MOCK-{doc_type.upper()}-{secrets.token_hex(4)}"
        doc.updated_at = datetime.utcnow()
    db.commit()

    return RedirectResponse(url="/settings?digilocker=success")


@router.get("/documents")
def get_digilocker_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.user_id == user.id, Document.source == "digilocker").all()
    return [{"doc_type": d.doc_type, "verified": d.verified, "doc_number": d.doc_number} for d in docs]


@router.post("/disconnect")
def disconnect(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.digilocker_connected = False
    db.commit()
    docs = db.query(Document).filter(Document.user_id == user.id, Document.source == "digilocker").all()
    for d in docs:
        d.source = "manual"
        d.verified = False
    db.commit()
    return {"message": "DigiLocker disconnected"}


@router.post("/refresh")
def refresh_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.digilocker_connected:
        return {"message": "DigiLocker not connected"}
    for doc_type in MOCK_DOCS:
        doc = db.query(Document).filter(Document.user_id == user.id, Document.doc_type == doc_type).first()
        if doc:
            doc.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Documents refreshed from DigiLocker"}