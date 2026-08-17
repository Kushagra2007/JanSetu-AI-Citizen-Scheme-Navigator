import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Profile, Document, Scheme
from auth import get_current_user
from scoring import compute_eligibility_score

router = APIRouter(prefix="/api/schemes", tags=["schemes"])


def scheme_to_dict(s: Scheme):
    return {
        "id": s.id, "name": s.name, "category": s.category, "description": s.description,
        "benefits": s.benefits, "min_age": s.min_age, "max_age": s.max_age,
        "max_income": s.max_income, "gender": s.gender,
        "caste_categories": json.loads(s.caste_categories or "[]"),
        "occupations": json.loads(s.occupations or "[]"),
        "states": json.loads(s.states or '["All"]'),
        "documents_required": json.loads(s.documents_required or "[]"),
        "deadline": s.deadline, "department": s.department, "official_url": s.official_url,
    }


@router.get("")
def list_schemes(category: str = None, db: Session = Depends(get_db)):
    q = db.query(Scheme)
    if category:
        q = q.filter(Scheme.category == category)
    return [scheme_to_dict(s) for s in q.all()]


@router.get("/recommended")
def recommended_schemes(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    documents = db.query(Document).filter(Document.user_id == user.id).all()
    schemes = db.query(Scheme).all()
    results = []
    for s in schemes:
        score = compute_eligibility_score(profile, documents, s)
        results.append({**scheme_to_dict(s), "score": score})
    results.sort(key=lambda r: r["score"]["total_score"], reverse=True)
    return results


@router.get("/saved")
def get_saved_schemes(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    ids = json.loads(profile.saved_schemes or "[]")
    schemes = db.query(Scheme).filter(Scheme.id.in_(ids)).all()
    return [scheme_to_dict(s) for s in schemes]


@router.get("/{scheme_id}")
def get_scheme(scheme_id: int, db: Session = Depends(get_db)):
    s = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme_to_dict(s)


@router.get("/{scheme_id}/eligibility")
def check_eligibility(scheme_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Scheme not found")
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    documents = db.query(Document).filter(Document.user_id == user.id).all()
    return compute_eligibility_score(profile, documents, s)


@router.post("/{scheme_id}/save")
def save_scheme(scheme_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    ids = json.loads(profile.saved_schemes or "[]")
    if scheme_id not in ids:
        ids.append(scheme_id)
    profile.saved_schemes = json.dumps(ids)
    db.commit()
    return {"message": "Scheme saved"}


@router.delete("/{scheme_id}/save")
def unsave_scheme(scheme_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    ids = json.loads(profile.saved_schemes or "[]")
    ids = [i for i in ids if i != scheme_id]
    profile.saved_schemes = json.dumps(ids)
    db.commit()
    return {"message": "Scheme removed from saved"}