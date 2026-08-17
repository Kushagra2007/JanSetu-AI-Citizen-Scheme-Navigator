from sqlalchemy.orm import Session
from models import Notification


def create_notification(db: Session, user_id: int, ntype: str, title: str, message: str, related_id: int = None):
    notif = Notification(
        user_id=user_id, type=ntype, title=title, message=message, related_id=related_id
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def notify_new_scheme(db: Session, user_id: int, scheme_name: str, scheme_id: int):
    return create_notification(
        db, user_id, "new_scheme", "New Scheme Available",
        f"A new scheme '{scheme_name}' may match your profile. Check it out!", scheme_id
    )


def notify_status_update(db: Session, user_id: int, app_name: str, new_status: str, app_id: int):
    return create_notification(
        db, user_id, "status_update", "Application Status Updated",
        f"Your application for '{app_name}' is now '{new_status}'.", app_id
    )


def notify_deadline(db: Session, user_id: int, scheme_name: str, deadline: str, scheme_id: int):
    return create_notification(
        db, user_id, "deadline", "Deadline Approaching",
        f"'{scheme_name}' deadline is {deadline}. Apply soon!", scheme_id
    )


def notify_document_missing(db: Session, user_id: int, doc_name: str):
    return create_notification(
        db, user_id, "document_missing", "Document Missing",
        f"You're missing '{doc_name}' which is required for some schemes/services.", None
    )