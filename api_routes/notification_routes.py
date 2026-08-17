from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Notification
from schemas import PushSubscription
from auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def notif_to_dict(n: Notification):
    return {
        "id": n.id, "type": n.type, "title": n.title, "message": n.message,
        "related_id": n.related_id, "read": n.read, "created_at": n.created_at.isoformat(),
    }


@router.get("")
def list_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifs = db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).all()
    return [notif_to_dict(n) for n in notifs]


@router.get("/unread-count")
def unread_count(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(Notification).filter(Notification.user_id == user.id, Notification.read == False).count()
    return {"unread_count": count}


@router.put("/{notif_id}/read")
def mark_read(notif_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    n = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user.id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    n.read = True
    db.commit()
    return {"message": "Marked as read"}


@router.put("/read-all")
def mark_all_read(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == user.id, Notification.read == False).update({"read": True})
    db.commit()
    return {"message": "All marked as read"}


@router.delete("/{notif_id}")
def delete_notification(notif_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    n = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user.id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(n)
    db.commit()
    return {"message": "Notification deleted"}


@router.post("/subscribe")
def subscribe_push(payload: PushSubscription, user: User = Depends(get_current_user)):
    # In production, persist subscription & integrate with web-push library.
    return {"message": "Push subscription registered (mock)", "endpoint": payload.endpoint}