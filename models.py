from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=False)
    token = Column(String, unique=True, index=True, nullable=True)
    language_pref = Column(String, default="en")
    dark_mode = Column(Boolean, default=False)
    digilocker_connected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("Profile", back_populates="user", uselist=False)
    documents = relationship("Document", back_populates="user")
    applications = relationship("Application", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    income = Column(Float, nullable=True)
    occupation = Column(String, nullable=True)
    state = Column(String, nullable=True)
    district = Column(String, nullable=True)
    category = Column(String, nullable=True)
    education = Column(String, nullable=True)
    marital_status = Column(String, nullable=True)
    disability = Column(Boolean, default=False)
    saved_schemes = Column(Text, default="[]")
    completeness = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    doc_type = Column(String)
    has_document = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    source = Column(String, default="manual")
    doc_number = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="documents")


class Scheme(Base):
    __tablename__ = "schemes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category = Column(String)
    description = Column(Text)
    benefits = Column(Text)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    max_income = Column(Float, nullable=True)
    gender = Column(String, default="All")
    caste_categories = Column(Text, default="[]")
    occupations = Column(Text, default="[]")
    states = Column(Text, default='["All"]')
    education = Column(Text, default="[]")
    marital_status = Column(String, default="Any")
    disability_required = Column(Boolean, default=False)
    documents_required = Column(Text, default="[]")
    deadline = Column(String, nullable=True)
    department = Column(String, nullable=True)
    official_url = Column(String, nullable=True)


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category = Column(String)
    description = Column(Text)
    fee = Column(String)
    duration_estimate = Column(String)
    steps = Column(Text)


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    ref_id = Column(Integer)
    ref_name = Column(String)
    status = Column(String, default="draft")
    current_step = Column(Integer, default=0)
    progress = Column(Text, default="[]")
    expected_completion = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="applications")


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    title = Column(String)
    message = Column(Text)
    related_id = Column(Integer, nullable=True)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String)
    sender = Column(String)
    message = Column(Text)
    intent = Column(String, nullable=True)
    entities = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_messages")