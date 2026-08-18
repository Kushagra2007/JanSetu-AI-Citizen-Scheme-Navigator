import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Service
from data.seed import ensure_reference_data

router = APIRouter(prefix="/api/services", tags=["services"])


def service_to_dict(s: Service, include_steps=True):
    d = {
        "id": s.id, "name": s.name, "category": s.category, "description": s.description,
        "fee": s.fee, "duration_estimate": s.duration_estimate,
    }
    if include_steps:
        d["steps"] = json.loads(s.steps or "[]")
    return d


@router.get("")
def list_services(db: Session = Depends(get_db)):
    ensure_reference_data(db)
    return [service_to_dict(s, include_steps=False) for s in db.query(Service).all()]


@router.get("/{service_id}")
def get_service(service_id: int, db: Session = Depends(get_db)):
    ensure_reference_data(db)
    s = db.query(Service).filter(Service.id == service_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    return service_to_dict(s)


@router.get("/{service_id}/pathway")
def get_pathway(service_id: int, db: Session = Depends(get_db)):
    ensure_reference_data(db)
    s = db.query(Service).filter(Service.id == service_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    steps = json.loads(s.steps or "[]")
    return {"service_name": s.name, "total_steps": len(steps), "steps": steps}
