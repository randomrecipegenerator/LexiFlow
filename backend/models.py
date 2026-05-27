import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Firm(Base):
    __tablename__ = "firms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    slug = Column(String, unique=True, index=True)
    branding_logo = Column(String, nullable=True)
    branding_colors = Column(Text, nullable=True) # JSON of colors
    api_config_json = Column(Text, nullable=True) # Store Clio/Filevine/OpenAI keys per firm
    
    # AI Front Desk Settings
    voice_enabled = Column(Integer, default=1)
    voice_config_json = Column(Text, nullable=True) # voice_id, greeting, etc.
    email_enabled = Column(Integer, default=1)
    email_config_json = Column(Text, nullable=True) # template, inbound_address, etc.
    active_hours_json = Column(Text, nullable=True) # Mon-Sun opening/closing times
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    plan_status = Column(String, default="pilot") # pilot, active, suspended
    trial_expires_at = Column(DateTime, nullable=True)
    production_sync_enabled = Column(Integer, default=0) # 0 for simulation, 1 for production sync

    users = relationship("User", back_populates="firm")
    leads = relationship("Lead", back_populates="firm")
    forms = relationship("Form", back_populates="firm")
    knowledge_base = relationship("KnowledgeBase", back_populates="firm")
    usage = relationship("Usage", back_populates="firm")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    firm_id = Column(Integer, ForeignKey("firms.id"))
    is_active = Column(Integer, default=1)
    role = Column(String, default="attorney") # admin, attorney, staff

    firm = relationship("Firm", back_populates="users")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=True) # Nullable for global demos
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

    firm = relationship("Firm", back_populates="leads")
    messages = relationship("Message", back_populates="lead")
    documents = relationship("Document", back_populates="lead")
    invoices = relationship("Invoice", back_populates="lead")
    audit_logs = relationship("AuditLog", back_populates="lead")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    action = Column(String) # esign_sent, invoice_created, lead_qualified, etc.
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    firm = relationship("Firm")
    lead = relationship("Lead", back_populates="audit_logs")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=True)
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
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    firm = Column(String, nullable=True) # Text name for free-form
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    firm_ref = relationship("Firm")

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
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=True)
    name = Column(String, index=True)
    branding_logo = Column(String, nullable=True)
    branding_colors = Column(String, nullable=True)
    qualification_rules = Column(Text, nullable=True) # Rules specific to this form
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    firm = relationship("Firm", back_populates="forms")
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
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=True)
    title = Column(String)
    content = Column(Text)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    firm = relationship("Firm", back_populates="knowledge_base")

class Usage(Base):
    __tablename__ = "usage"

    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firms.id"))
    usage_type = Column(String) # document_analysis, voice_minutes, email_intake
    quantity = Column(Float, default=1.0)
    details = Column(Text, nullable=True) # Optional JSON details
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    firm = relationship("Firm", back_populates="usage")
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="uploaded") # uploaded, processing, completed, error
    
    facts = relationship("Fact", back_populates="transcript")
    conflicts = relationship("Conflict", back_populates="transcript")
    summaries = relationship("Summary", back_populates="transcript")

class Fact(Base):
    __tablename__ = "facts"
    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id"))
    witness_name = Column(String)
    date_time = Column(String)
    event_description = Column(Text)
    page_reference = Column(Integer)
    line_reference = Column(Integer)
    
    transcript = relationship("Transcript", back_populates="facts")

class Conflict(Base):
    __tablename__ = "conflicts"
    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id"))
    witness_a = Column(String)
    witness_b = Column(String)
    description = Column(Text)
    reasoning = Column(Text)
    severity = Column(String) # High, Medium, Low
    
    transcript = relationship("Transcript", back_populates="conflicts")

class Summary(Base):
    __tablename__ = "summaries"
    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id"))
    admissions = Column(Text)
    risks = Column(Text)
    executive_summary = Column(Text)
    
    transcript = relationship("Transcript", back_populates="summaries")

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="uploaded") # uploaded, processing, completed, error
    reports = relationship("MeritReport", back_populates="record")

class MeritReport(Base):
    __tablename__ = "merit_reports"
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("medical_records.id"))
    chronology = Column(Text)
    negligence_markers = Column(Text)
    standard_of_care_analysis = Column(Text)
    executive_summary = Column(Text)
    record = relationship("MedicalRecord", back_populates="reports")
