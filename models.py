import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Firm(Base):
    __tablename__ = "firms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    slug = Column(String, unique=True, index=True)
    branding_logo = Column(String, nullable=True)
    branding_colors = Column(Text, nullable=True)
    api_config_json = Column(Text, nullable=True)
    voice_enabled = Column(Integer, default=1)
    voice_config_json = Column(Text, nullable=True)
    email_enabled = Column(Integer, default=1)
    email_config_json = Column(Text, nullable=True)
    active_hours_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    plan_status = Column(String, default="pilot")
    trial_expires_at = Column(DateTime, nullable=True)
    production_sync_enabled = Column(Integer, default=0)
    billing_tier = Column(String, default="standard")
    billing_period_start = Column(DateTime, default=datetime.datetime.utcnow)
    document_count = Column(Integer, default=0)
    ocr_page_count = Column(Integer, default=0)

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
    role = Column(String, default="attorney")
    phone = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    invite_token = Column(String, nullable=True)
    invite_accepted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    firm = relationship("Firm", back_populates="users")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=True)
    full_name = Column(String, index=True, nullable=True)
    email = Column(String, index=True, nullable=True)
    phone = Column(String, index=True, nullable=True)
    case_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    qualification_score = Column(Float, default=0.0)
    status = Column(String, default="New")
    ai_summary = Column(Text, nullable=True)
    source = Column(String, default="Chat")
    is_demo = Column(Integer, default=0)
    esign_request_id = Column(String, nullable=True)
    esign_status = Column(String, default="Not Sent")
    sync_status = Column(String, default="Not Synced")
    external_crm_id = Column(String, nullable=True)
    case_value_estimate = Column(Float, default=0.0)
    demand_letter_draft = Column(Text, nullable=True)
    consent_given = Column(Integer, default=0)
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    action = Column(String, index=True)
    category = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    firm = relationship("Firm")
    user = relationship("User")
    lead = relationship("Lead", back_populates="audit_logs")

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    amount = Column(Float)
    currency = Column(String, default="USD")
    status = Column(String, default="Pending")
    external_id = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    lead = relationship("Lead", back_populates="invoices")

class DemoRequest(Base):
    __tablename__ = "demo_requests"
    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    firm = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    firm_ref = relationship("Firm")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    role = Column(String)
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
    extracted_data_json = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    lead = relationship("Lead", back_populates="documents")

class Form(Base):
    __tablename__ = "forms"
    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=True)
    name = Column(String, index=True)
    branding_logo = Column(String, nullable=True)
    branding_colors = Column(String, nullable=True)
    qualification_rules = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    firm = relationship("Firm", back_populates="forms")
    questions = relationship("Question", back_populates="form")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id"))
    text = Column(String)
    type = Column(String)
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
    usage_type = Column(String)
    quantity = Column(Float, default=1.0)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    firm = relationship("Firm", back_populates="usage")

class UsageRecord(Base):
    __tablename__ = "usage_records"
    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firms.id"), index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    document_type = Column(String, index=True)
    document_name = Column(String, nullable=True)
    page_count = Column(Integer, default=0)
    processing_time_ms = Column(Integer, default=0)
    ai_tokens_used = Column(Integer, default=0)
    overage_eligible = Column(Boolean, default=True)
    billing_period = Column(String, index=True)
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)
    firm = relationship("Firm")
    lead = relationship("Lead")

class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="uploaded")
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
    severity = Column(String)
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
    status = Column(String, default="uploaded")
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