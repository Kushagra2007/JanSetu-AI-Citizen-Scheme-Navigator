import json
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Scheme, Service, User, Profile
from data.schemes_data import SCHEMES
from data.services_data import SERVICES
from auth import get_optional_user, hash_password, generate_token

from api_routes import (
    auth_routes, profile_routes, chat_routes, scheme_routes,
    service_routes, application_routes, notification_routes, digilocker_routes,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Citizen Service Navigator", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

for r in [auth_routes.router, profile_routes.router, chat_routes.router, scheme_routes.router,
          service_routes.router, application_routes.router, notification_routes.router,
          digilocker_routes.router]:
    app.include_router(r)


@app.on_event("startup")
def seed_data():
    db: Session = next(get_db())

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

    if db.query(Scheme).count() == 0:
        for s in SCHEMES:
            db.add(Scheme(
                name=s["name"], category=s["category"], description=s["description"],
                benefits=s["benefits"], min_age=s["min_age"], max_age=s["max_age"],
                max_income=s["max_income"], gender=s["gender"],
                caste_categories=json.dumps(s["caste_categories"]),
                occupations=json.dumps(s["occupations"]), states=json.dumps(s["states"]),
                education=json.dumps(s["education"]), marital_status=s["marital_status"],
                disability_required=s["disability_required"],
                documents_required=json.dumps(s["documents_required"]),
                deadline=s["deadline"], department=s["department"], official_url=s["official_url"],
            ))
    if db.query(Service).count() == 0:
        for sv in SERVICES:
            db.add(Service(
                name=sv["name"], category=sv["category"], description=sv["description"],
                fee=sv["fee"], duration_estimate=sv["duration_estimate"],
                steps=json.dumps(sv["steps"]),
            ))
    db.commit()
    db.close()


# ---------- Page routes (HTML) ----------

@app.get("/")
def landing(request: Request, user=Depends(get_optional_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/login")
def login_page(request: Request, user=Depends(get_optional_user)):
    if user:
        return RedirectResponse("/chat")
    return templates.TemplateResponse("login.html", {"request": request, "user": None})


@app.get("/register")
def register_page(request: Request, user=Depends(get_optional_user)):
    if user:
        return RedirectResponse("/chat")
    return templates.TemplateResponse("register.html", {"request": request, "user": None})


@app.get("/chat")
def chat_page(request: Request, user=Depends(get_optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("chat.html", {"request": request, "user": user})


@app.get("/profile")
def profile_page(request: Request, user=Depends(get_optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})


@app.get("/schemes")
def schemes_page(request: Request, user=Depends(get_optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("schemes.html", {"request": request, "user": user})


@app.get("/service/{service_id}")
def service_page(service_id: int, request: Request, user=Depends(get_optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("service.html", {"request": request, "user": user, "service_id": service_id})


@app.get("/applications")
def applications_page(request: Request, user=Depends(get_optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("applications.html", {"request": request, "user": user})


@app.get("/notifications")
def notifications_page(request: Request, user=Depends(get_optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("notifications.html", {"request": request, "user": user})


@app.get("/settings")
def settings_page(request: Request, user=Depends(get_optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("settings.html", {"request": request, "user": user})


@app.get("/health")
def health():
    return {"status": "ok"}