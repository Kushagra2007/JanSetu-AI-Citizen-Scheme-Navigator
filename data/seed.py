"""Idempotent seed helpers for the built-in scheme and service catalogue."""
import json

from data.schemes_data import SCHEMES
from data.services_data import SERVICES
from models import Scheme, Service


def ensure_reference_data(db) -> None:
    changed = False
    known_schemes = {name for (name,) in db.query(Scheme.name).all()}
    for s in SCHEMES:
        if s["name"] not in known_schemes:
            db.add(Scheme(
            name=s["name"], category=s["category"], description=s["description"], benefits=s["benefits"],
            min_age=s["min_age"], max_age=s["max_age"], max_income=s["max_income"], gender=s["gender"],
            caste_categories=json.dumps(s["caste_categories"]), occupations=json.dumps(s["occupations"]),
            states=json.dumps(s["states"]), education=json.dumps(s["education"]),
            marital_status=s["marital_status"], disability_required=s["disability_required"],
            documents_required=json.dumps(s["documents_required"]), deadline=s["deadline"],
            department=s["department"], official_url=s["official_url"],
            ))
            changed = True
    known_services = {name for (name,) in db.query(Service.name).all()}
    for s in SERVICES:
        if s["name"] not in known_services:
            db.add(Service(
            name=s["name"], category=s["category"], description=s["description"], fee=s["fee"],
            duration_estimate=s["duration_estimate"], steps=json.dumps(s["steps"]),
            ))
            changed = True
    if changed:
        db.commit()
