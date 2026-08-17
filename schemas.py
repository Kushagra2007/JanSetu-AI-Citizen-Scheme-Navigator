from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    language_pref: Optional[str] = "en"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    income: Optional[float] = None
    occupation: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    category: Optional[str] = None
    education: Optional[str] = None
    marital_status: Optional[str] = None
    disability: Optional[bool] = None


class DocumentUpdate(BaseModel):
    doc_type: str
    has_document: bool
    doc_number: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ApplicationCreate(BaseModel):
    type: str  # scheme / service
    ref_id: int


class ApplicationStepUpdate(BaseModel):
    step_index: int
    completed: bool


class ApplicationStatusUpdate(BaseModel):
    status: str


class PushSubscription(BaseModel):
    endpoint: str
    keys: Dict[str, str]