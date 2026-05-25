from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=True)
    email = Column(String, index=True, nullable=True)
    phone = Column(String, index=True, nullable=True)
    case_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    qualification_score = Column(Float, default=0.0)
    status = Column(String, default="New") # New, Qualified, Disqualified, Requires Review
    ai_summary = Column(Text, nullable=True)
    source = Column(String, default="Chat") # Chat, Form, Receptionist
    is_demo = Column(Integer, default=0) # 0 for real, 1 for demo
    esign_request_id = Column(String, nullable=True)
    esign_status = Column(String, default="Not Sent") # Not Sent, Pending, Signed, Declined
    sync_status = Column(String, default="Not Synced") # Not Synced, Synced, Error
    external_crm_id = Column(String, nullable=True)
    case_value_estimate = Column(Float, default=0.0)
    demand_letter_draft = Column(Text, nullable=True)
    consent_given = Column(Integer, default=0) # 0 for no, 1 for yes
    consent_timestamp = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    messages = relationship("Message", back_populates="lead")
    documents = relationship("Document", back_populates="lead")
    invoices = relationship("Invoice", back_populates="lead")
    audit_logs = relationship("AuditLog", back_populates="lead")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    action = Column(String) # esign_sent, invoice_created, lead_qualified, etc.
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    lead = relationship("Lead", back_populates="audit_logs")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    amount = Column(Float)
    currency = Column(String, default="USD")
    status = Column(String, default="Pending") # Pending, Paid, Cancelled
    external_id = Column(String, nullable=True) # ID from LawPay/Stripe
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    lead = relationship("Lead", back_populates="invoices")

class DemoRequest(Base):
    __tablename__ = "demo_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    firm = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    role = Column(String) # user, assistant
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    lead = relationship("Lead", back_populates="messages")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    filename = Column(String)
    file_path = Column(String)
    extracted_text = Column(Text, nullable=True)
    extracted_data_json = Column(Text, nullable=True) # JSON of extracted fields
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    lead = relationship("Lead", back_populates="documents")

class Form(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    branding_logo = Column(String, nullable=True)
    branding_colors = Column(String, nullable=True)
    qualification_rules = Column(Text, nullable=True) # Rules specific to this form
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    questions = relationship("Question", back_populates="form")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id"))
    text = Column(String)
    type = Column(String) # text, date, yes_no
    logic_json = Column(Text, nullable=True)
    order = Column(Integer)

    form = relationship("Form", back_populates="questions")

class FormResponse(Base):
    __tablename__ = "form_responses"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id"))
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    answers_json = Column(Text)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
