import json
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import Base, engine, get_db, SessionLocal
from models import ChatMessage, Scheme, Service, User, Profile
from data.schemes_data import SCHEMES
from data.services_data import SERVICES
from data.seed import ensure_reference_data
from auth import get_optional_user, hash_password, generate_token

from api_routes import (
    auth_routes, profile_routes, chat_routes, scheme_routes,
    service_routes, application_routes, notification_routes, digilocker_routes,
)


def init_db():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        if db.query(User).count() == 0:
            demo_user = User(
                name="Demo User",
                email="demo@jansetu.in",
                phone="9999999999",
                password_hash=hash_password("demo123"),
                token=generate_token(),
                language_pref="en",
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            db.add(Profile(user_id=demo_user.id))

        ensure_reference_data(db)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Citizen Service Navigator", version="1.0.0", lifespan=lifespan)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

for r in [auth_routes.router, profile_routes.router, chat_routes.router, scheme_routes.router,
          service_routes.router, application_routes.router, notification_routes.router,
          digilocker_routes.router]:
    app.include_router(r)


# ---------- Page routes (HTML) ----------

@app.get("/")
def landing(request: Request, user=Depends(get_optional_user)):
    return templates.TemplateResponse(request, "index.html", {"user": user})


@app.get("/login")
def login_page(request: Request, user=Depends(get_optional_user)):
    return templates.TemplateResponse(request, "login.html", {"user": None})


@app.get("/register")
def register_page(request: Request, user=Depends(get_optional_user)):
    return templates.TemplateResponse(request, "register.html", {"user": None})


@app.get("/chat")
def chat_page(request: Request, user=Depends(get_optional_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse("/login")
    history = (db.query(ChatMessage)
               .filter(ChatMessage.user_id == user.id)
               .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
               .all())
    return templates.TemplateResponse(request, "chat.html", {"user": user, "history": history})


@app.get("/profile")
def profile_page(request: Request, user=Depends(get_optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(request, "profile.html", {"user": user})


@app.get("/schemes")
def schemes_page(request: Request, user=Depends(get_optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(request, "schemes.html", {"user": user})


@app.get("/services")
def services_page(request: Request, user=Depends(get_optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(request, "services.html", {"user": user})


@app.get("/service/{service_id}")
def service_page(service_id: int, request: Request, user=Depends(get_optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(request, "service.html", {"user": user, "service_id": service_id})


@app.get("/applications")
def applications_page(request: Request, user=Depends(get_optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(request, "applications.html", {"user": user})


@app.get("/notifications")
def notifications_page(request: Request, user=Depends(get_optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(request, "notifications.html", {"user": user})


@app.get("/settings")
def settings_page(request: Request, user=Depends(get_optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(request, "settings.html", {"user": user})


@app.get("/health")
def health():
    return {"status": "ok"}
