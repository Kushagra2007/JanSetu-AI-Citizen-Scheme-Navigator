import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Profile, Document
from schemas import ProfileUpdate, DocumentUpdate
from auth import get_current_user
from scoring import compute_profile_completeness

router = APIRouter(prefix="/api/profile", tags=["profile"])

DOC_TYPES = ["aadhaar", "pan", "bank", "passport", "driving_license", "voter_id", "ration_card"]


@router.get("")
def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    docs = db.query(Document).filter(Document.user_id == user.id).all()
    doc_map = {d.doc_type: {"has_document": d.has_document, "verified": d.verified, "source": d.source} for d in docs}
    for dt in DOC_TYPES:
        doc_map.setdefault(dt, {"has_document": False, "verified": False, "source": "manual"})

    return {
        "age": profile.age, "gender": profile.gender, "income": profile.income,
        "occupation": profile.occupation, "state": profile.state, "district": profile.district,
        "category": profile.category, "education": profile.education,
        "marital_status": profile.marital_status, "disability": profile.disability,
        "completeness": profile.completeness,
        "saved_schemes": json.loads(profile.saved_schemes or "[]"),
        "documents": doc_map,
    }


@router.put("")
def update_profile(payload: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    profile.completeness = compute_profile_completeness(profile)
    db.commit()
    db.refresh(profile)
    return {"message": "Profile updated", "completeness": profile.completeness}


@router.put("/documents")
def update_document(payload: DocumentUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.user_id == user.id, Document.doc_type == payload.doc_type).first()
    if not doc:
        doc = Document(user_id=user.id, doc_type=payload.doc_type)
        db.add(doc)
    doc.has_document = payload.has_document
    doc.doc_number = payload.doc_number
    doc.source = "manual"
    db.commit()
    return {"message": "Document updated"}


@router.get("/completeness")
def get_completeness(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    score = compute_profile_completeness(profile)
    profile.completeness = score
    db.commit()
    return {"completeness": score}