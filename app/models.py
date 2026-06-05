import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.database import Base

def utcnow(): return datetime.now(timezone.utc)
def gen_uuid(): return str(uuid.uuid4())

class Firm(Base):
    __tablename__ = "firms"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    subscription_tier = Column(String(50), nullable=False, default="basic")
    settings = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    users = relationship("User", back_populates="firm", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="firm", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_uuid)
    firm_id = Column(String, ForeignKey("firms.id"), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="attorney")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    firm = relationship("Firm", back_populates="users")

class Lead(Base):
    __tablename__ = "leads"
    id = Column(String, primary_key=True, default=gen_uuid)
    firm_id = Column(String, ForeignKey("firms.id"), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    case_type = Column(String(100), nullable=True)
    incident_description = Column(Text, nullable=True)
    state = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False, default="new")
    source = Column(String(100), nullable=True, default="widget")
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    firm = relationship("Firm", back_populates="leads")

class LeadQualification(Base):
    __tablename__ = "lead_qualifications"
    id = Column(String, primary_key=True, default=gen_uuid)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False, unique=True, index=True)
    overall_score = Column(Float, nullable=False)
    liability_score = Column(Float, nullable=True)
    damages_score = Column(Float, nullable=True)
    medical_merit_score = Column(Float, nullable=True)
    reasoning_summary = Column(Text, nullable=True)
    key_strengths = Column(JSON, nullable=True)
    key_risks = Column(JSON, nullable=True)
    recommended_action = Column(String(50), nullable=True)
    ai_model_used = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    lead = relationship("Lead", backref="qualification", uselist=False)