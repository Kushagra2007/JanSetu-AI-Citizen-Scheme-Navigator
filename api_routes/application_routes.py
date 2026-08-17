import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Application, Scheme, Service
from schemas import ApplicationCreate, ApplicationStepUpdate, ApplicationStatusUpdate
from auth import get_current_user
from notifications import notify_status_update

router = APIRouter(prefix="/api/applications", tags=["applications"])

STATUS_FLOW = ["draft", "submitted", "review", "approved", "rejected", "completed"]


def app_to_dict(a: Application):
    return {
        "id": a.id, "type": a.type, "ref_id": a.ref_id, "ref_name": a.ref_name,
        "status": a.status, "current_step": a.current_step,
        "progress": json.loads(a.progress or "[]"),
        "expected_completion": a.expected_completion.isoformat() if a.expected_completion else None,
        "created_at": a.created_at.isoformat(), "updated_at": a.updated_at.isoformat(),
    }


@router.post("")
def create_application(payload: ApplicationCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.type == "scheme":
        ref = db.query(Scheme).filter(Scheme.id == payload.ref_id).first()
        num_steps = 4
    else:
        ref = db.query(Service).filter(Service.id == payload.ref_id).first()
        num_steps = len(json.loads(ref.steps or "[]")) if ref else 6

    if not ref:
        raise HTTPException(status_code=404, detail="Reference scheme/service not found")

    progress = [{"step": i, "completed": False} for i in range(num_steps)]
    application = Application(
        user_id=user.id, type=payload.type, ref_id=payload.ref_id, ref_name=ref.name,
        status="draft", current_step=0, progress=json.dumps(progress),
        expected_completion=datetime.utcnow() + timedelta(days=30),
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return app_to_dict(application)


@router.get("")
def list_applications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    apps = db.query(Application).filter(Application.user_id == user.id).order_by(Application.created_at.desc()).all()
    return [app_to_dict(a) for a in apps]


@router.get("/{app_id}")
def get_application(app_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_to_dict(a)


@router.put("/{app_id}/status")
def update_status(app_id: int, payload: ApplicationStatusUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Application not found")
    if payload.status not in STATUS_FLOW:
        raise HTTPException(status_code=400, detail="Invalid status")
    a.status = payload.status
    db.commit()
    notify_status_update(db, user.id, a.ref_name, a.status, a.id)
    return app_to_dict(a)


@router.put("/{app_id}/step")
def update_step(app_id: int, payload: ApplicationStepUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Application not found")
    progress = json.loads(a.progress or "[]")
    for p in progress:
        if p["step"] == payload.step_index:
            p["completed"] = payload.completed
    a.progress = json.dumps(progress)
    completed_count = sum(1 for p in progress if p["completed"])
    a.current_step = completed_count
    if completed_count == len(progress) and progress:
        a.status = "completed"
        notify_status_update(db, user.id, a.ref_name, "completed", a.id)
    elif a.status == "draft" and completed_count > 0:
        a.status = "submitted"
    db.commit()
    return app_to_dict(a)


@router.delete("/{app_id}")
def delete_application(app_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(a)
    db.commit()
    return {"message": "Application deleted"}