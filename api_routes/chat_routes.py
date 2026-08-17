import json
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Profile, ChatMessage
from schemas import ChatRequest
from auth import get_current_user
from nlp_engine import process_message
from scoring import compute_profile_completeness

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message")
def send_message(payload: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    profile_ctx = {"age": profile.age, "state": profile.state} if profile else {}

    result = process_message(payload.message, language=user.language_pref, profile_ctx=profile_ctx)

    user_msg = ChatMessage(
        user_id=user.id, session_id=payload.session_id, sender="user",
        message=payload.message, intent=result["intent"], entities=json.dumps(result["entities"]),
    )
    db.add(user_msg)

    # Auto-update profile from extracted entities
    entities = result["entities"]
    updated_fields = []
    if profile:
        field_map = {"age": "age", "income": "income", "state": "state", "category": "category",
                     "occupation": "occupation", "gender": "gender", "education": "education",
                     "marital_status": "marital_status", "disability": "disability"}
        for ent_key, prof_field in field_map.items():
            if ent_key in entities:
                setattr(profile, prof_field, entities[ent_key])
                updated_fields.append(prof_field)
        if updated_fields:
            profile.completeness = compute_profile_completeness(profile)

    bot_msg = ChatMessage(
        user_id=user.id, session_id=payload.session_id, sender="bot",
        message=result["response"], intent=result["intent"], entities=json.dumps(entities),
    )
    db.add(bot_msg)
    db.commit()

    return {
        "response": result["response"], "intent": result["intent"],
        "confidence": result["confidence"], "entities": entities,
        "updated_profile_fields": updated_fields,
    }


@router.get("/history")
def get_history(session_id: str = "default", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    messages = (db.query(ChatMessage)
                .filter(ChatMessage.user_id == user.id, ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc()).all())
    return [{"sender": m.sender, "message": m.message, "intent": m.intent,
             "created_at": m.created_at.isoformat()} for m in messages]


@router.delete("/history")
def clear_history(session_id: str = "default", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(ChatMessage).filter(ChatMessage.user_id == user.id, ChatMessage.session_id == session_id).delete()
    db.commit()
    return {"message": "History cleared"}


@router.get("/new-session")
def new_session():
    return {"session_id": str(uuid.uuid4())}