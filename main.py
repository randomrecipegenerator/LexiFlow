import logging

logger = logging.getLogger(__name__)

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Header, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
import uuid
import httpx
import json
import asyncio
from datetime import datetime

import models, database, ai_engine, esign_engine, integration_engine, reception_engine, utils, reports
import enterprise_api, desktop_api, admin_api, billing_api
from auth import auth_router
from database import engine, get_db
from health_diagnostics import health_diagnostics, HealthDiagnostics

def create_audit_log(db: Session, action: str, lead_id: int = None, details: str = None, firm_id: int = None):
    log = models.AuditLog(lead_id=lead_id, action=action, details=details, firm_id=firm_id)
    db.add(log)
    db.commit()

# Dependency to get current firm (for dashboard/authenticated routes)
def get_current_firm(db: Session = Depends(get_db), x_firm_slug: str = Header(None)):
    if not x_firm_slug:
        return None
    firm = db.query(models.Firm).filter(models.Firm.slug == x_firm_slug).first()
    return firm

# Helper to find firm by slug (for public intake routes)
def find_firm_by_slug(db: Session, slug: str):
    if not slug:
        return None
    return db.query(models.Firm).filter(models.Firm.slug == slug).first()

app = FastAPI(title="LexiFlow API")

async def event_generator():
    while True:
        # Send a heartbeat every 15 seconds to keep the connection alive
        # Some proxies (like E2B or Vercel) might close idle connections
        yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
        await asyncio.sleep(15)

@app.get("/__engine/events")
async def engine_events():
    """
    Real-time event stream for the LexiFlow Engine.
    Used for live updates on document processing, lead qualification, and CRM sync.
    """
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.middleware("http")
async def standardize_path(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api/"):
        request.scope["path"] = path[4:]
        logger.error(f"MIDDLEWARE: Stripped /api/ from {path} -> {request.scope['path']}")
    response = await call_next(request)
    return response

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=engine)

@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Enhanced health check with Enterprise Suite diagnostics."""
    try:
        diagnostics = await health_diagnostics.check_all()
        return diagnostics
    except Exception as e:
        logger.warning(f"Health diagnostics failed, returning basic: {e}")
        return {
            "status": "healthy",
            "environment": "vercel" if os.getenv("VERCEL") else "local",
            "diagnostics_unavailable": str(e),
        }

# CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from other modules
app.include_router(enterprise_api.router)
app.include_router(desktop_api.router)
app.include_router(auth_router)
app.include_router(admin_api.router)

app.include_router(billing_api.router)
app.include_router(billing_api.webhook_router)
try:
    from usage_api import router as usage_router
    app.include_router(usage_router)
except ImportError:
    pass  # Usage API optional for now

# Indentation fix
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.getenv("VERCEL"):
    UPLOAD_DIR = "/tmp/uploads"
    # Ensure tables are created only once or handled by the startup event
    # metadata.create_all is usually safe to call multiple times with SQLite
else:
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))

if not os.path.exists(UPLOAD_DIR):
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    except:
        pass # Ignore errors if directory can't be created on read-only FS
# API Endpoints

@app.post("/chat/start")
def start_chat(firm_slug: str = None, db: Session = Depends(get_db)):
    firm = find_firm_by_slug(db, firm_slug)
    lead = models.Lead(firm_id=firm.id if firm else None)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return {"lead_id": lead.id}


@app.post("/v1/intake/submit")
async def case_intake_submit(
    firm_name: str = Form(...),
    attorney_email: str = Form(...),
    case_type: str = Form(...),
    jurisdiction: str = Form(...),
    case_summary: str = Form(...),
    estimated_damages: float = Form(None),
    firm_slug: str = Form(None),
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/intake/submit
    
    Public endpoint for the 'Submit a Case for AI Merit Review' form.
    Accepts case details, creates a Lead, runs AI merit scoring,
    and returns the score and summary.
    
    Accessible via /api/v1/intake/submit (middleware strips /api/ prefix).
    """
    # 1. Find or create the firm
    firm = None
    if firm_slug:
        firm = db.query(models.Firm).filter(models.Firm.slug == firm_slug).first()
    if not firm:
        firm = db.query(models.Firm).filter(models.Firm.name.ilike(f"%{firm_name}%")).first()
    if not firm:
        firm = db.query(models.Firm).filter(
            models.Firm.api_config_json.ilike(f"%{firm_name}%")
        ).first()

    # 2. Create the Lead record
    lead = models.Lead(
        firm_id=firm.id if firm else None,
        full_name=firm_name if not firm else f"{firm_name} Lead",
        email=attorney_email,
        case_type=case_type.replace("-", " ").title(),
        description=case_summary,
        case_value_estimate=estimated_damages or 0.0,
        source="Web Intake Form",
        status="New",
    )
    db.add(lead)
    db.flush()

    # 3. Run AI merit scoring
    kb_context = ""
    if firm:
        kb_entries = db.query(models.KnowledgeBase).filter(
            models.KnowledgeBase.is_active == 1,
            models.KnowledgeBase.firm_id == firm.id,
        ).all()
        kb_context = "\n".join([f"KB - {k.title}: {k.content}" for k in kb_entries])

    score, status, summary, client_info, case_value = ai_engine.qualify_lead(
        case_summary, context=kb_context
    )

    # 4. Save AI results to the Lead
    lead.qualification_score = score
    lead.status = status
    lead.ai_summary = summary
    if case_value and not estimated_damages:
        lead.case_value_estimate = case_value

    if firm:
        utils.log_usage(db, firm.id, "web_intake", quantity=1.0, details=f"Web Intake Form: Lead ID {lead.id}")

    db.commit()

    # 5. Log audit
    create_audit_log(
        db, "case_intake_submit", lead.id,
        f"Firm: {firm_name}, Type: {case_type}, Score: {score}, Status: {status}",
        firm_id=firm.id if firm else None,
    )

    # 6. Auto-sync to CRM if score is high enough
    if score >= 70 and firm:
        try:
            import asyncio
            await asyncio.sleep(0)  # Allow event loop to yield
            sync_result = await integration_engine.integration_engine.sync_lead_auto(lead, db=db)
            if sync_result.get("targets"):
                create_audit_log(
                    db, "intake_auto_sync", lead.id,
                    f"Score: {score}, Targets: {sync_result['targets']}",
                    firm_id=firm.id,
                )
        except Exception as e:
            logger.warning(f"Auto-sync skipped for lead {lead.id}: {e}")

    return {
        "status": "success",
        "lead_id": lead.id,
        "merit_score": score,
        "merit_summary": summary,
        "case_status": status,
        "firm_linked": bool(firm),
        "firm_name": firm.name if firm else None,
        "estimated_value": lead.case_value_estimate,
    }


@app.post("/demo-request")
async def demo_request(name: str = Form(...), email: str = Form(...), firm: str = Form(None), tier: str = Form(None), db: Session = Depends(get_db)):
    demo_req = models.DemoRequest(name=name, email=email, firm=firm)
    db.add(demo_req)
    db.commit()
    
    # Send notification email to the sales team
    subject = f"New Consultation Request: {name}"
    body = f"""
    You have a new consultation request from the LexiFlow website.
    
    Name: {name}
    Email: {email}
    Law Firm: {firm or 'Not provided'}
    Plan Tier: {tier or 'Not specified'}
    
    Timestamp: {demo_req.created_at}
    """
    
    # Also create a more professional HTML version
    html_body = f"""
    <h2>New LexiFlow Consultation Request</h2>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Law Firm:</strong> {firm or 'Not provided'}</p>
    <p><strong>Plan Tier:</strong> {tier or 'Not specified'}</p>
    <hr>
    <p><small>Received at {demo_req.created_at}</small></p>
    """
    
    try:
        from mail_service import mail_service
        await mail_service.send_email(
            to_email="lexiflow-legal-suite-88a6f8e9@ctomail.io",
            subject=subject,
            body=body,
            html_body=html_body
        )
    except Exception as e:
        # Log error but don't block the user's request
        logger.error(f"Failed to send demo request notification: {e}")

    create_audit_log(db, "demo_request", details=f"Name: {name}, Email: {email}, Firm: {firm}, Tier: {tier}")
    return {"status": "success", "message": "Demo request received"}

@app.post("/integrations/github/push")
async def github_push(
    repo: str = Form(...),
    branch: str = Form("main"),
    path: str = Form(...),
    content: str = Form(...),
    commit_message: str = Form("LexiFlow Export"),
    db: Session = Depends(get_db),
    current_firm: models.Firm = Depends(get_current_firm)
):
    if not current_firm:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    result = await integration_engine.integration_engine.push_to_github(
        firm=current_firm,
        repo_full_name=repo,
        branch=branch,
        file_path=path,
        content=content,
        commit_message=commit_message
    )
    
    if result["status"] == "success":
        create_audit_log(db, "github_export", details=f"Repo: {repo}, Path: {path}", firm_id=current_firm.id)
        
    return result

@app.post("/demo/seed")
def seed_demo_leads(firm_slug: str = Form("general"), db: Session = Depends(get_db)):
    firm = db.query(models.Firm).filter(models.Firm.slug == firm_slug).first()
    if not firm:
        raise HTTPException(status_code=404, detail=f"Firm with slug '{firm_slug}' not found. Please provision it first.")

    # Delete existing demo leads for this firm to refresh
    db.query(models.Lead).filter(models.Lead.is_demo == 1, models.Lead.firm_id == firm.id).delete()
    
    demo_leads = []
    
    if firm.slug == "smith-lacien":
        demo_leads = [
            models.Lead(
                firm_id=firm.id,
                full_name="Todd's High-Value Lead (MedMal)",
                email="victim.medical@example.com",
                phone="312-555-9000",
                case_type="Medical Malpractice",
                description="Surgical complication at Chicago Memorial. Retained instrument post-op.",
                qualification_score=98.5,
                status="High Priority",
                ai_summary="Extreme negligence case. Smith LaCien's expertise in high-verdict MedMal is perfectly suited here. Liability is clear.",
                is_demo=1
            ),
            models.Lead(
                firm_id=firm.id,
                full_name="Truck Collision: Route 66",
                email="driver.hit@gmail.com",
                phone="312-555-4444",
                case_type="Personal Injury - Trucking",
                description="Jackknifed semi-truck on I-55. Client sustained multiple fractures and head trauma.",
                qualification_score=94.2,
                status="High Priority",
                ai_summary="High-stakes trucking accident. Logbook violations suspected. Strong liability against the carrier.",
                is_demo=1
            ),
            models.Lead(
                firm_id=firm.id,
                full_name="Maria Rodriguez (Spanish Intake)",
                email="m.rodriguez@example.com",
                phone="312-555-2233",
                case_type="Medical Malpractice / Birth Injury",
                description="Negligencia médica durante el parto en el Hospital San Lucas. El bebé tiene parálisis cerebral.",
                qualification_score=99.0,
                status="High Priority",
                ai_summary="Spanish language intake. Severe birth injury case (Cerebral Palsy). High emotional and legal stakes. Smith LaCien's multilingual support is critical here.",
                is_demo=1
            )
        ]
    elif firm.slug == "clifford-law":
        demo_leads = [
            models.Lead(
                firm_id=firm.id,
                full_name="Mass Tort: Flight 402 Claimant",
                email="claimant@mass-tort-hub.com",
                phone="312-555-1111",
                case_type="Aviation/Mass Tort",
                description="Family member of a passenger on the recent international flight incident.",
                qualification_score=95.0,
                status="High Priority",
                ai_summary="Direct victim's family. Clifford Law is the lead counsel for this incident. High-value lead.",
                is_demo=1
            ),
            models.Lead(
                firm_id=firm.id,
                full_name="Product Liability: Defective Valve",
                email="consumer.hurt@outlook.com",
                phone="312-555-8888",
                case_type="Product Liability",
                description="Heart valve failure in a 45-year-old patient. Model was recently recalled.",
                qualification_score=91.0,
                status="High Priority",
                ai_summary="Clear product defect case with recent recall evidence. High potential for significant damages.",
                is_demo=1
            )
        ]
    else:
        demo_leads = [
            models.Lead(
                firm_id=firm.id,
                full_name="Standard PI Lead",
                email="john.doe@example.com",
                phone="555-000-1111",
                case_type="Car Accident",
                description="Rear-ended at a stoplight. Neck and back pain.",
                qualification_score=75.0,
                status="Qualified",
                ai_summary="Straightforward car accident. Liability likely 100% on other driver.",
                is_demo=1
            )
        ]
    
    for lead in demo_leads:
        db.add(lead)
        db.flush()
        msg1 = models.Message(lead_id=lead.id, role="assistant", content=f"Hello! I'm Lexi, the AI assistant for {firm.name}. I'm here to help.")
        msg2 = models.Message(lead_id=lead.id, role="user", content=lead.description)
        msg3 = models.Message(lead_id=lead.id, role="assistant", content="I've recorded all the details for our legal team.")
        db.add_all([msg1, msg2, msg3])
        
        create_audit_log(db, "demo_lead_seeded", lead.id, f"Firm: {firm.name}", firm_id=firm.id)

    db.commit()
    return {"status": "success", "message": f"Demo leads seeded for {firm.name}"}

@app.get("/reports/stats")
def get_report_stats(db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    if not current_firm:
        raise HTTPException(status_code=401, detail="Authentication required")
    return reports.get_weekly_stats(db, current_firm.id)

@app.post("/reports/trigger")
async def trigger_report(db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    if not current_firm:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    result = await reports.generate_and_send_report(db, current_firm)
    
    create_audit_log(db, "report_triggered", details=f"Recipient: {result.get('recipient')}", firm_id=current_firm.id)
    
    return result

@app.get("/demo/firms")
def get_demo_firms(db: Session = Depends(get_db)):
    firms = db.query(models.Firm).all()
    return [{"name": f.name, "slug": f.slug} for f in firms]

@app.get("/firm/me")
def get_current_firm_details(current_firm: models.Firm = Depends(get_current_firm)):
    if not current_firm:
        # Return default branding if no firm selected
        return {
            "name": "LexiFlow Pro",
            "slug": "general",
            "branding_logo": "/branding/logo-icon.svg",
            "branding_colors": json.dumps({
                "primary": "#2563eb",
                "secondary": "#1e40af"
            })
        }
    return {
        "name": current_firm.name,
        "slug": current_firm.slug,
        "branding_logo": current_firm.branding_logo,
        "branding_colors": current_firm.branding_colors,
        "voice_enabled": current_firm.voice_enabled,
        "voice_config": json.loads(current_firm.voice_config_json) if current_firm.voice_config_json else {},
        "email_enabled": current_firm.email_enabled,
        "email_config": json.loads(current_firm.email_config_json) if current_firm.email_config_json else {},
        "active_hours": json.loads(current_firm.active_hours_json) if current_firm.active_hours_json else {},
        "production_sync_enabled": current_firm.production_sync_enabled,
        "api_config": json.loads(current_firm.api_config_json) if current_firm.api_config_json else {}
    }

@app.get("/firm/onboarding")
def get_onboarding_status(db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    if not current_firm:
        # For demo purposes, if no firm is logged in
        return {
            "checklist": [
                {
                    "id": "branding",
                    "title": "Customize Branding",
                    "description": "Upload your firm logo and set your primary brand colors.",
                    "status": "pending",
                    "action_text": "Configure",
                    "action_link": "settings"
                }
            ],
            "overall_progress": 0
        }
    
    # 1. Branding
    branding_complete = bool(current_firm.branding_logo and current_firm.branding_colors)
    
    # 2. Integrations
    api_config = {}
    if current_firm.api_config_json:
        try:
            api_config = json.loads(current_firm.api_config_json)
        except:
            pass
    
    github_connected = bool(api_config.get("github_token"))
    postmark_connected = bool(api_config.get("postmark_api_key"))
    
    # 3. Domain (Placeholder/Mock)
    domain_verified = api_config.get("domain_verified", False)
    
    # 4. Activity
    lead_count = db.query(models.Lead).filter(models.Lead.firm_id == current_firm.id).count()
    doc_count = db.query(models.Document).join(models.Lead).filter(models.Lead.firm_id == current_firm.id).count()
    
    checklist = [
        {
            "id": "branding",
            "title": "Customize Branding",
            "description": "Upload your firm logo and set your primary brand colors.",
            "status": "completed" if branding_complete else "pending",
            "action_text": "Update Branding" if branding_complete else "Go to Settings",
            "action_link": "settings"
        },
        {
            "id": "github",
            "title": "Configure GitHub Export",
            "description": "Connect your GitHub repository to export case summaries automatically.",
            "status": "completed" if github_connected else "pending",
            "action_text": "Connect GitHub",
            "action_link": "settings"
        },
        {
            "id": "postmark",
            "title": "Verify Email Notifications",
            "description": "Set up Postmark to receive instant email alerts for new leads.",
            "status": "completed" if postmark_connected else "pending",
            "action_text": "Configure Postmark",
            "action_link": "settings"
        },
        {
            "id": "domain",
            "title": "Verify Website Domain",
            "description": "Add our snippet to your website to start capturing leads 24/7.",
            "status": "completed" if domain_verified else "pending",
            "action_text": "Get Snippet",
            "action_link": "front-desk"
        },
        {
            "id": "test-lead",
            "title": "Capture First Lead",
            "description": "Generate a test lead using the AI Chat or Voice assistant.",
            "status": "completed" if lead_count > 0 else "pending",
            "action_text": "Try AI Chat",
            "action_link": "leads"
        },
        {
            "id": "test-doc",
            "title": "Analyze Medical Record",
            "description": "Upload a medical record to test the AI document analysis engine.",
            "status": "completed" if doc_count > 0 else "pending",
            "action_text": "Upload Document",
            "action_link": "leads"
        }
    ]
    
    return {
        "checklist": checklist,
        "overall_progress": int((sum(1 for item in checklist if item["status"] == "completed") / len(checklist)) * 100)
    }

@app.post("/firm/settings")
def update_firm_settings(
    voice_enabled: int = Form(None),
    voice_config: str = Form(None),
    email_enabled: int = Form(None),
    email_config: str = Form(None),
    active_hours: str = Form(None),
    production_sync_enabled: int = Form(None),
    api_config: str = Form(None),
    db: Session = Depends(get_db),
    current_firm: models.Firm = Depends(get_current_firm)
):
    if not current_firm:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if voice_enabled is not None:
        current_firm.voice_enabled = voice_enabled
    if voice_config:
        current_firm.voice_config_json = voice_config
    if email_enabled is not None:
        current_firm.email_enabled = email_enabled
    if email_config:
        current_firm.email_config_json = email_config
    if active_hours:
        current_firm.active_hours_json = active_hours
    if production_sync_enabled is not None:
        current_firm.production_sync_enabled = production_sync_enabled
    if api_config:
        current_firm.api_config_json = api_config
    
    db.commit()
    create_audit_log(db, "settings_updated", details="Firm settings updated via dashboard", firm_id=current_firm.id)
    return {"status": "success"}

@app.post("/sync/{system}/{lead_id}")
async def universal_sync(system: str, lead_id: int, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.Lead).filter(models.Lead.id == lead_id)
    if current_firm:
        query = query.filter(models.Lead.firm_id == current_firm.id)
    lead = query.first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    result = await integration_engine.integration_engine.sync_lead(lead, system)
    
    if result["status"] == "success":
        lead.sync_status = f"Synced ({system.capitalize()})"
        if "external_id" in result:
            lead.external_crm_id = result["external_id"]
        elif result.get("simulated"):
             lead.external_crm_id = f"sim_{uuid.uuid4().hex[:8]}"
    else:
        lead.sync_status = "Error"

    db.commit()
    
    create_audit_log(db, f"sync_{system}", lead_id, f"Result: {result['status']}")
    
    return result

@app.post("/chat/message")
def send_message(lead_id: int, content: str = Form(...), db: Session = Depends(get_db)):
    # Save user message
    user_msg = models.Message(lead_id=lead_id, role="user", content=content)
    db.add(user_msg)
    db.commit()
    
    # Get conversation history
    messages = db.query(models.Message).filter(models.Message.lead_id == lead_id).order_by(models.Message.timestamp.asc()).all()
    history = [{"role": m.role, "content": m.content} for m in messages]
    
    # Fetch Knowledge Base context
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    kb_context = ""
    if lead:
        kb_entries = db.query(models.KnowledgeBase).filter(models.KnowledgeBase.is_active == 1)
        if lead.firm_id:
            kb_entries = kb_entries.filter(models.KnowledgeBase.firm_id == lead.firm_id)
        kb_entries = kb_entries.all()
        kb_context = "\n".join([f"KB - {k.title}: {k.content}" for k in kb_entries])
    
    # Get AI response
    ai_content = ai_engine.get_ai_response(history, context=kb_context)
    
    # Save AI message
    ai_msg = models.Message(lead_id=lead_id, role="assistant", content=ai_content)
    db.add(ai_msg)
    
    # Update lead info if possible (simple extraction for MVP)
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if "name is" in content.lower():
        lead.full_name = content.lower().split("name is")[-1].strip()
    
    db.commit()
    return {"content": ai_content}

@app.post("/chat/upload")
async def upload_file(lead_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1]
    filename = f"{file_id}.{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Extract text if it's a PDF or Image
    extracted_text = None
    extracted_data = None
    
    if extension.lower() == "pdf":
        extracted_text = ai_engine.extract_text_from_pdf(file_path)
        if extracted_text:
            extracted_data = ai_engine.analyze_document_text(extracted_text, file.filename)
    elif extension.lower() in ["jpg", "jpeg", "png"]:
        extracted_data = ai_engine.analyze_document_image(file_path, file.filename)
        if extracted_data and "summary" in extracted_data:
            extracted_text = extracted_data["summary"]
    
    doc = models.Document(
        lead_id=lead_id, 
        filename=file.filename, 
        file_path=file_path, 
        extracted_text=extracted_text,
        extracted_data_json=json.dumps(extracted_data) if extracted_data else None
    )
    db.add(doc)
    
    # Update Lead profile if we found key data
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if lead and lead.firm_id:
        utils.log_usage(db, lead.firm_id, "document_analysis", quantity=1.0, details=f"File: {file.filename}")

    if extracted_data and "extracted_fields" in extracted_data:
        lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
        fields = extracted_data["extracted_fields"]
        if not lead.full_name and ("name" in fields or "full_name" in fields):
            lead.full_name = fields.get("name") or fields.get("full_name")
        if not lead.email and "email" in fields:
            lead.email = fields.get("email")
        if not lead.phone and "phone" in fields:
            lead.phone = fields.get("phone")
        
        # Change status to 'Document Analysis' or similar if needed
        lead.status = "Document Analysis"
    
    db.commit()
    
    create_audit_log(db, "document_uploaded", lead_id, f"File: {file.filename}, Type: {extension}")
    
    return {"filename": file.filename, "status": "uploaded", "analysis": extracted_data}

@app.post("/chat/complete")
def complete_chat(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    messages = db.query(models.Message).filter(models.Message.lead_id == lead_id).order_by(models.Message.timestamp.asc()).all()
    transcript = "\n".join([f"{m.role}: {m.content}" for m in messages])
    
    # Include document text in analysis
    docs = db.query(models.Document).filter(models.Document.lead_id == lead_id).all()
    doc_context = ""
    for d in docs:
        if d.extracted_text:
            doc_context += f"\n--- Document: {d.filename} ---\n{d.extracted_text}\n"
    
    full_transcript = transcript + "\n" + doc_context
    
    # Fetch Knowledge Base context
    kb_entries = db.query(models.KnowledgeBase).filter(models.KnowledgeBase.is_active == 1)
    if lead.firm_id:
        kb_entries = kb_entries.filter(models.KnowledgeBase.firm_id == lead.firm_id)
    kb_entries = kb_entries.all()
    kb_context = "\n".join([f"KB - {k.title}: {k.content}" for k in kb_entries])
    
    score, status, summary, client_info, case_value = ai_engine.qualify_lead(full_transcript, context=kb_context)
    
    lead.qualification_score = score
    lead.status = status
    lead.ai_summary = summary
    lead.case_value_estimate = case_value
    
    if lead.firm_id:
        utils.log_usage(db, lead.firm_id, "web_intake", quantity=1.0, details=f"Lead ID: {lead_id}")
    
    if client_info:
        if not lead.full_name and client_info.get("full_name"):
            lead.full_name = client_info.get("full_name")
        if not lead.email and client_info.get("email"):
            lead.email = client_info.get("email")
        if not lead.phone and client_info.get("phone"):
            lead.phone = client_info.get("phone")
            
    db.commit()
    
    create_audit_log(db, "lead_qualified", lead_id, f"Score: {score}, Status: {status}")
    
    # Auto-sync to configured CRMs based on qualification score
    try:
        import asyncio
        sync_result = asyncio.run(integration_engine.integration_engine.sync_lead_auto(lead, db=db))
        if sync_result.get("targets"):
            create_audit_log(db, "lead_auto_sync", lead_id, f"Score: {score}, Targets: {sync_result['targets']}, Results: {sync_result['results']}")
    except Exception as e:
        print(f"Auto-sync failed for lead {lead_id}: {str(e)}")
    
    return {"status": status, "score": score}

@app.get("/leads", response_model=List[dict])
def get_leads(demo_mode: bool = False, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.Lead)
    
    if current_firm:
        query = query.filter(models.Lead.firm_id == current_firm.id)
    
    if demo_mode:
        query = query.filter(models.Lead.is_demo == 1)
    else:
        query = query.filter(models.Lead.is_demo == 0)
    
    leads = query.order_by(models.Lead.created_at.desc()).all()
    result = []
    for l in leads:
        result.append({
            "id": l.id,
            "full_name": l.full_name or "Anonymous",
            "email": l.email,
            "status": l.status,
            "source": l.source,
            "score": l.qualification_score,
            "sync_status": l.sync_status,
            "created_at": l.created_at.isoformat(),
            "summary": l.ai_summary
        })
    return result

@app.get("/leads/{lead_id}")
def get_lead_detail(lead_id: int, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.Lead).filter(models.Lead.id == lead_id)
    if current_firm:
        query = query.filter(models.Lead.firm_id == current_firm.id)
    
    lead = query.first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    messages = db.query(models.Message).filter(models.Message.lead_id == lead_id).order_by(models.Message.timestamp.asc()).all()
    docs = db.query(models.Document).filter(models.Document.lead_id == lead_id).all()
    
    return {
        "id": lead.id,
        "full_name": lead.full_name,
        "email": lead.email,
        "phone": lead.phone,
        "status": lead.status,
        "source": lead.source,
        "score": lead.qualification_score,
        "summary": lead.ai_summary,
        "case_value": lead.case_value_estimate,
        "demand_draft": lead.demand_letter_draft,
        "sync_status": lead.sync_status,
        "external_crm_id": lead.external_crm_id,
        "messages": [{"role": m.role, "content": m.content, "time": m.timestamp.isoformat()} for m in messages],
        "documents": [
            {
                "filename": d.filename, 
                "path": d.file_path, 
                "extracted_text": d.extracted_text,
                "analysis": json.loads(d.extracted_data_json) if d.extracted_data_json else None
            } for d in docs
        ],
        "invoices": [{"id": i.id, "amount": i.amount, "currency": i.currency, "status": i.status, "date": i.created_at.isoformat()} for i in lead.invoices],
        "esign_status": lead.esign_status
    }


@app.post("/forms")
def create_form(name: str = Form(...), branding_logo: str = Form(None), branding_colors: str = Form(None), questions_json: str = Form(...), db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    firm_id = current_firm.id if current_firm else None
    form = models.Form(name=name, branding_logo=branding_logo, branding_colors=branding_colors, firm_id=firm_id)
    db.add(form)
    db.flush()
    
    questions_data = json.loads(questions_json)
    temp_to_real_id = {}
    
    # First pass: Create all questions and store the mapping
    created_questions = []
    for q_data in questions_data:
        question = models.Question(
            form_id=form.id,
            text=q_data['text'],
            type=q_data['type'],
            order=questions_data.index(q_data)
        )
        db.add(question)
        created_questions.append((question, q_data))
        
    db.flush() # Get all real IDs
    
    for question, q_data in created_questions:
        temp_to_real_id[q_data['id']] = question.id
        
    # Second pass: Update logic with real IDs
    for question, q_data in created_questions:
        logic = q_data.get('logic')
        if logic and 'dependsOn' in logic:
            temp_dep_id = logic['dependsOn']
            if temp_dep_id in temp_to_real_id:
                logic['dependsOn'] = temp_to_real_id[temp_dep_id]
        
        question.logic_json = json.dumps(logic)
    
    db.commit()
    return {"form_id": form.id}

@app.get("/forms")
def get_forms(db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.Form)
    if current_firm:
        query = query.filter(models.Form.firm_id == current_firm.id)
    return query.all()

@app.get("/forms/{form_id}")
def get_form(form_id: int, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.Form).filter(models.Form.id == form_id)
    if current_firm:
        query = query.filter(models.Form.firm_id == current_firm.id)
    
    form = query.first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    questions = db.query(models.Question).filter(models.Question.form_id == form_id).order_by(models.Question.order.asc()).all()
    return {
        "id": form.id,
        "name": form.name,
        "branding_logo": form.branding_logo,
        "branding_colors": form.branding_colors,
        "questions": [
            {
                "id": q.id,
                "text": q.text,
                "type": q.type,
                "logic": json.loads(q.logic_json) if q.logic_json else None
            } for q in questions
        ]
    }

@app.post("/forms/{form_id}/submit")
def submit_form(form_id: int, answers_json: str = Form(...), db: Session = Depends(get_db)):
    form = db.query(models.Form).filter(models.Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
        
    answers = json.loads(answers_json) # dict of question_id: answer
    
    # Create a lead
    name = answers.get('name') or answers.get('full_name')
    if not name:
        # Try to find a question that might be the name
        name = "Form Lead"
    
    lead = models.Lead(full_name=name, firm_id=form.firm_id)
    db.add(lead)
    db.flush()
    
    # Save response
    response = models.FormResponse(form_id=form_id, lead_id=lead.id, answers_json=answers_json)
    db.add(response)
    
    # AI Scoring
    context = f"Dynamic Form Submission (Form ID: {form_id})\n\n"
    for q_id, answer in answers.items():
        if q_id.isdigit():
            question = db.query(models.Question).filter(models.Question.id == int(q_id)).first()
            if question:
                context += f"Question: {question.text}\nAnswer: {answer}\n\n"
        else:
            context += f"{q_id}: {answer}\n\n"
            
    score, status, summary, client_info, case_value = ai_engine.qualify_lead(context, context=form.qualification_rules)
    lead.qualification_score = score
    lead.status = status
    lead.ai_summary = summary
    lead.case_value_estimate = case_value
    
    if form.firm_id:
        utils.log_usage(db, form.firm_id, "form_intake", quantity=1.0, details=f"Form ID: {form_id}, Lead ID: {lead.id}")
    
    db.commit()
    return {"status": "success", "lead_id": lead.id}

@app.post("/reception/webhook")
async def reception_webhook(
    name: str = Form(...), 
    email: str = Form(None), 
    phone: str = Form(None), 
    notes: str = Form(None), 
    source: str = Form("Receptionist"),
    firm_slug: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Endpoint for virtual receptionists (e.g., Ruby, Smith.ai) to push lead info.
    """
    firm = find_firm_by_slug(db, firm_slug)
    lead = models.Lead(
        full_name=name, 
        email=email, 
        phone=phone, 
        description=notes, 
        source=source,
        firm_id=firm.id if firm else None
    )
    db.add(lead)
    db.flush()
    
    # AI Qualification
    kb_entries = db.query(models.KnowledgeBase).filter(models.KnowledgeBase.is_active == 1)
    if lead.firm_id:
        kb_entries = kb_entries.filter(models.KnowledgeBase.firm_id == lead.firm_id)
    kb_entries = kb_entries.all()
    kb_context = "\n".join([f"KB - {k.title}: {k.content}" for k in kb_entries])
    
    score, status, summary, client_info, case_value = ai_engine.qualify_lead(f"Receptionist Notes: {notes}", context=kb_context)
    lead.qualification_score = score
    lead.status = status
    lead.ai_summary = summary
    lead.case_value_estimate = case_value
    
    if client_info:
        if not lead.full_name and client_info.get("full_name"):
            lead.full_name = client_info.get("full_name")
        if not lead.email and client_info.get("email"):
            lead.email = client_info.get("email")
        if not lead.phone and client_info.get("phone"):
            lead.phone = client_info.get("phone")
    
    if lead.firm_id:
        utils.log_usage(db, lead.firm_id, "receptionist_intake", quantity=1.0, details=f"Source: {source}, Lead ID: {lead.id}")
    
    db.commit()
    
    create_audit_log(db, "reception_sync", lead.id, f"Source: {source}")
    
    return {"status": "success", "lead_id": lead.id}

# --- Voice AI Endpoints ---

@app.get("/voice/calls", response_model=List[dict])
def get_voice_calls(db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.VoiceCall)
    if current_firm:
        query = query.filter(models.VoiceCall.firm_id == current_firm.id)
    calls = query.order_by(models.VoiceCall.created_at.desc()).all()
    
    result = []
    for c in calls:
        result.append({
            "id": c.id,
            "lead_id": c.lead_id,
            "phone_number": c.phone_number,
            "recording_url": c.recording_url,
            "summary": c.summary,
            "transcript": c.transcript,
            "duration": c.duration_seconds,
            "status": c.status,
            "created_at": c.created_at.isoformat(),
            "lead_name": c.lead.full_name if c.lead else "Unknown",
            "qualification_score": c.lead.qualification_score if c.lead else 0
        })
    return result

@app.get("/voice/config")
def get_voice_config(db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    if not current_firm:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {
        "voice_enabled": current_firm.voice_enabled,
        "config": json.loads(current_firm.voice_config_json) if current_firm.voice_config_json else {}
    }

@app.post("/voice/config")
def update_voice_config(config: dict, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    if not current_firm:
        raise HTTPException(status_code=401, detail="Unauthorized")
    current_firm.voice_config_json = json.dumps(config)
    db.commit()
    return {"status": "success"}

# --- End Voice AI Endpoints ---

@app.post("/reception/vapi/brain")
async def vapi_brain(payload: dict, db: Session = Depends(get_db)):
    """Vapi Server URL for Voice AI logic"""
    result = await reception_engine.handle_vapi_message(payload, db)
    
    # If lead was created, try auto-syncing to CRMs
    if result.get("status") == "success" and result.get("lead_id"):
        lead = db.query(models.Lead).filter(models.Lead.id == result["lead_id"]).first()
        if lead and lead.qualification_score and lead.qualification_score >= 50:
            await integration_engine.integration_engine.sync_lead_auto(lead, db)
            
    return result

@app.post("/reception/postmark/inbound")
async def postmark_inbound(payload: dict, db: Session = Depends(get_db)):
    """Postmark Inbound Webhook for Email leads"""
    return await reception_engine.handle_postmark_inbound(payload, db)

@app.get("/knowledge-base")
def get_kb(db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.KnowledgeBase)
    if current_firm:
        query = query.filter(models.KnowledgeBase.firm_id == current_firm.id)
    return query.all()

@app.post("/knowledge-base")
def add_kb(title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    kb = models.KnowledgeBase(
        title=title, 
        content=content,
        firm_id=current_firm.id if current_firm else None
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb

@app.delete("/knowledge-base/{kb_id}")
def delete_kb(kb_id: int, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.KnowledgeBase).filter(models.KnowledgeBase.id == kb_id)
    if current_firm:
        query = query.filter(models.KnowledgeBase.firm_id == current_firm.id)
    
    kb = query.first()
    if not kb:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(kb)
    db.commit()
    return {"status": "success"}

@app.get("/billing/invoices")
def get_invoices(db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.Invoice)
    if current_firm:
        query = query.filter(models.Invoice.firm_id == current_firm.id)
    return query.all()

@app.post("/billing/invoices")
def create_invoice(lead_id: int = Form(...), amount: float = Form(...), currency: str = Form("USD"), description: str = Form(None), db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    lead_query = db.query(models.Lead).filter(models.Lead.id == lead_id)
    if current_firm:
        lead_query = lead_query.filter(models.Lead.firm_id == current_firm.id)
    
    lead = lead_query.first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    invoice = models.Invoice(
        lead_id=lead_id, 
        amount=amount, 
        currency=currency, 
        description=description,
        firm_id=current_firm.id if current_firm else lead.firm_id
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    # Simulate LawPay integration by generating an external ID
    invoice.external_id = f"lp_{uuid.uuid4().hex[:8]}"
    db.commit()
    
    create_audit_log(db, "invoice_created", lead_id, f"Amount: {amount} {currency}", firm_id=invoice.firm_id)
    
    return invoice

@app.post("/billing/sync/lawpay/{invoice_id}")
def sync_lawpay(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Simulate payment success
    invoice.status = "Paid"
    db.commit()
    
    return {"status": "success", "message": "Invoice synced with LawPay and marked as Paid"}

# eSignature Endpoints
@app.post("/esign/send/{lead_id}")
def send_esign_request(lead_id: int, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.Lead).filter(models.Lead.id == lead_id)
    if current_firm:
        query = query.filter(models.Lead.firm_id == current_firm.id)
    lead = query.first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    result = esign_engine.esign_client.create_embedded_signature_request(
        lead_name=lead.full_name,
        lead_email=lead.email
    )
    
    lead.esign_request_id = result["signature_request_id"]
    lead.esign_status = "Pending"
    db.commit()
    
    create_audit_log(db, "esign_sent", lead_id, f"Request ID: {result['signature_request_id']}")
    
    return result

@app.get("/esign/status/{lead_id}")
def get_esign_status(lead_id: int, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.Lead).filter(models.Lead.id == lead_id)
    if current_firm:
        query = query.filter(models.Lead.firm_id == current_firm.id)
    lead = query.first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if not lead.esign_request_id:
        return {"status": "Not Sent"}
    
    # In a real app, we might poll the API or rely on webhooks
    # For simulation, we'll just return the current DB status
    return {"status": lead.esign_status, "request_id": lead.esign_request_id}

@app.post("/esign/webhook")
async def esign_webhook(db: Session = Depends(get_db)):
    # Simulated webhook handler
    # In reality, Dropbox Sign sends a multipart form with a 'json' field
    # For now, we'll just provide a way to manually trigger a 'Signed' status for demo purposes
    return {"status": "success"}

@app.post("/esign/simulate_signed/{lead_id}")
def simulate_esign_signed(lead_id: int, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.Lead).filter(models.Lead.id == lead_id)
    if current_firm:
        query = query.filter(models.Lead.firm_id == current_firm.id)
    lead = query.first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead.esign_status = "Signed"
    db.commit()
    
    create_audit_log(db, "esign_signed", lead_id, "Simulated status update")
    
    return {"status": "success", "message": "Lead status updated to Signed"}

@app.get("/leads/{lead_id}/export/clio")
def export_lead_clio_csv(lead_id: int, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    """Export lead in Clio-compatible CSV format"""
    query = db.query(models.Lead).filter(models.Lead.id == lead_id)
    if current_firm:
        query = query.filter(models.Lead.firm_id == current_firm.id)
    lead = query.first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    import csv
    import io
    from fastapi.responses import StreamingResponse

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Clio Lead Import Headers (Common)
    headers = ["First Name", "Last Name", "Email", "Phone Number", "Note", "Source", "Status"]
    writer.writerow(headers)
    
    name_parts = (lead.full_name or "Anonymous").split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else "Lead"
    
    note = f"AI Summary: {lead.ai_summary}\n\nTranscript available in LexiFlow dashboard."
    
    writer.writerow([
        first_name,
        last_name,
        lead.email or "",
        lead.phone or "",
        note,
        lead.source or "LexiFlow Technologies Inc",
        lead.status or "New"
    ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=clio_lead_{lead_id}.csv"}
    )

@app.get("/billing/usage")
def get_usage(db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    if not current_firm:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    usage_entries = db.query(models.Usage).filter(models.Usage.firm_id == current_firm.id).order_by(models.Usage.timestamp.desc()).all()
    
    # Calculate totals by type
    totals = {}
    for entry in usage_entries:
        totals[entry.usage_type] = totals.get(entry.usage_type, 0) + entry.quantity
    
    return {
        "plan_status": current_firm.plan_status,
        "trial_expires_at": current_firm.trial_expires_at.isoformat() if current_firm.trial_expires_at else None,
        "totals": totals,
        "history": [
            {
                "type": e.usage_type,
                "quantity": e.quantity,
                "details": e.details,
                "timestamp": e.timestamp.isoformat()
            } for e in usage_entries
        ]
    }

@app.get("/admin/usage-report")
def get_admin_usage_report(db: Session = Depends(get_db)):
    """Global usage report for all firms (Admin only)"""
    firms = db.query(models.Firm).all()
    report = []
    for firm in firms:
        usage_entries = db.query(models.Usage).filter(models.Usage.firm_id == firm.id).all()
        totals = {}
        for entry in usage_entries:
            totals[entry.usage_type] = totals.get(entry.usage_type, 0) + entry.quantity
            
        report.append({
            "firm_id": firm.id,
            "firm_name": firm.name,
            "firm_slug": firm.slug,
            "plan_status": firm.plan_status,
            "totals": totals
        })
    return report

# GDPR & Compliance Endpoints
@app.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    """Right to be Forgotten - GDPR Compliance"""
    query = db.query(models.Lead).filter(models.Lead.id == lead_id)
    if current_firm:
        query = query.filter(models.Lead.firm_id == current_firm.id)
    lead = query.first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Delete related records (cascade delete is better but explicit for safety here)
    db.query(models.Message).filter(models.Message.lead_id == lead_id).delete()
    db.query(models.Document).filter(models.Document.lead_id == lead_id).delete()
    db.query(models.Invoice).filter(models.Invoice.lead_id == lead_id).delete()
    db.query(models.AuditLog).filter(models.AuditLog.lead_id == lead_id).delete()
    db.query(models.FormResponse).filter(models.FormResponse.lead_id == lead_id).delete()
    
    db.delete(lead)
    db.commit()
    
    # Log global action without lead_id reference since it's deleted
    create_audit_log(db, "data_deletion", details=f"Lead ID {lead_id} permanently deleted (GDPR)")
    
    return {"status": "success", "message": f"Lead {lead_id} and all related data deleted."}

@app.get("/leads/{lead_id}/export")
def export_lead_data(lead_id: int, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    """Data Portability - GDPR Compliance"""
    query = db.query(models.Lead).filter(models.Lead.id == lead_id)
    if current_firm:
        query = query.filter(models.Lead.firm_id == current_firm.id)
    lead = query.first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    messages = db.query(models.Message).filter(models.Message.lead_id == lead_id).all()
    invoices = db.query(models.Invoice).filter(models.Invoice.lead_id == lead_id).all()
    
    data = {
        "lead_info": {
            "id": lead.id,
            "full_name": lead.full_name,
            "email": lead.email,
            "phone": lead.phone,
            "case_type": lead.case_type,
            "description": lead.description,
            "created_at": lead.created_at.isoformat()
        },
        "transcript": [{"role": m.role, "content": m.content, "time": m.timestamp.isoformat()} for m in messages],
        "financials": [{"amount": i.amount, "currency": i.currency, "status": i.status} for i in invoices],
        "compliance": {
            "esign_status": lead.esign_status,
            "esign_id": lead.esign_request_id
        }
    }
    
    create_audit_log(db, "data_export", lead_id, "User requested data portability export")
    
    return data

@app.post("/leads/{lead_id}/draft-demand")
def generate_demand_draft(lead_id: int, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.Lead).filter(models.Lead.id == lead_id)
    if current_firm:
        query = query.filter(models.Lead.firm_id == current_firm.id)
    lead = query.first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    messages = db.query(models.Message).filter(models.Message.lead_id == lead_id).order_by(models.Message.timestamp.asc()).all()
    transcript = "\n".join([f"{m.role}: {m.content}" for m in messages])
    
    draft = ai_engine.draft_demand_letter(transcript)
    lead.demand_letter_draft = draft
    
    if lead.firm_id:
        utils.log_usage(db, lead.firm_id, "document_analysis", quantity=1.0, details=f"Demand Letter Draft (Lead ID: {lead_id})")
        
    db.commit()
    
    create_audit_log(db, "demand_draft_generated", lead_id)
    
    return {"draft": draft}

@app.get("/leads/{lead_id}/medical-chronology")
def get_medical_chronology(lead_id: int, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.Lead).filter(models.Lead.id == lead_id)
    if current_firm:
        query = query.filter(models.Lead.firm_id == current_firm.id)
    lead = query.first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    messages = db.query(models.Message).filter(models.Message.lead_id == lead_id).order_by(models.Message.timestamp.asc()).all()
    transcript = "\n".join([f"{m.role}: {m.content}" for m in messages])
    
    chronology = ai_engine.generate_medical_chronology(transcript)
    
    if lead.firm_id:
        utils.log_usage(db, lead.firm_id, "document_analysis", quantity=1.0, details=f"Medical Chronology (Lead ID: {lead_id})")
        
    create_audit_log(db, "medical_chronology_generated", lead_id)
    
    return {"chronology": chronology}

# --- MeritScan Logic ---
def process_meritscan_task(record_id: int, db_session: Session):
    try:
        record = db_session.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()
        if not record: return
        record.status = "processing"
        db_session.commit()
        
        # Load file content
        with open(record.file_path, "r", errors="ignore") as f:
            text = f.read()
            
        report_data = ai_engine.generate_merit_report(text)
        
        report = models.MeritReport(
            record_id=record.id,
            chronology=report_data.get("chronology", ""),
            negligence_markers=report_data.get("negligence_markers", ""),
            standard_of_care_analysis=report_data.get("standard_of_care_analysis", ""),
            executive_summary=report_data.get("executive_summary", "")
        )
        db_session.add(report)
        record.status = "completed"
        db_session.commit()
    except Exception as e:
        print(f"MeritScan Processing Error: {e}")
        if record:
            record.status = "error"
            db_session.commit()

@app.post("/meritscan/upload")
async def meritscan_upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"merit_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    record = models.MedicalRecord(filename=file.filename, file_path=file_path)
    db.add(record)
    db.commit()
    db.refresh(record)
    background_tasks.add_task(process_meritscan_task, record.id, db)
    return {"id": record.id, "filename": record.filename, "status": record.status}

@app.get("/meritscan/reports")
def list_merit_reports(db: Session = Depends(get_db)):
    return db.query(models.MedicalRecord).all()

@app.get("/meritscan/reports/{id}")
def get_merit_report(id: int, db: Session = Depends(get_db)):
    record = db.query(models.MedicalRecord).filter(models.MedicalRecord.id == id).first()
    if not record: raise HTTPException(status_code=404, detail="Record not found")
    report = db.query(models.MeritReport).filter(models.MeritReport.record_id == id).first()
    return {"record": record, "report": report}
# --- End MeritScan ---

# --- Veritas Deposition™ (formerly Veritas Deposition™) Endpoints ---
def process_transcript_task(transcript_id: int, db: Session):
    transcript = db.query(models.Transcript).filter(models.Transcript.id == transcript_id).first()
    if not transcript: return
    try:
        transcript.status = "processing"
        db.commit()
        text = ""
        if transcript.filename.lower().endswith(".pdf"):
            text = ai_engine.extract_text_from_pdf(transcript.file_path)
        else:
            with open(transcript.file_path, "r") as f:
                text = f.read()
        analysis = ai_engine.analyze_transcript(text)
        for f in analysis.get("chronology", []):
            fact = models.Fact(
                transcript_id=transcript_id,
                witness_name=f.get("Witness Name") or f.get("witness_name"),
                date_time=f.get("Date and Time") or f.get("date_time"),
                event_description=f.get("Event Description") or f.get("event_description"),
                page_reference=f.get("Page Reference") or f.get("page_reference")
            )
            db.add(fact)
        for c in analysis.get("conflicts", []):
            conflict = models.Conflict(
                transcript_id=transcript_id,
                witness_a=c.get("Witness A") or c.get("witness_a"),
                witness_b=c.get("Witness B") or c.get("witness_b"),
                description=c.get("Conflict Description") or c.get("description"),
                reasoning=c.get("Reasoning") or c.get("reasoning"),
                severity=c.get("Severity") or c.get("severity")
            )
            db.add(conflict)
        s = analysis.get("summary", {})
        summary = models.Summary(
            transcript_id=transcript_id,
            admissions=s.get("admissions"),
            risks=s.get("risks"),
            executive_summary=s.get("executive_summary")
        )
        db.add(summary)
        transcript.status = "completed"
        db.commit()
    except Exception as e:
        print(f"Veritas Deposition™ Processing Error: {e}")
        transcript.status = "error"
        db.commit()

@app.post("/veritas/upload")
@app.post("/depolens/upload")
async def veritas_upload(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    transcript = models.Transcript(filename=file.filename, file_path=file_path)
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    background_tasks.add_task(process_transcript_task, transcript.id, db)
    return {"id": transcript.id, "filename": transcript.filename, "status": transcript.status}

@app.get("/veritas/transcripts")
@app.get("/depolens/transcripts")
def list_transcripts(db: Session = Depends(get_db)):
    return db.query(models.Transcript).all()

@app.get("/veritas/transcripts/{id}")
@app.get("/depolens/transcripts/{id}")
def get_transcript(id: int, db: Session = Depends(get_db)):
    transcript = db.query(models.Transcript).filter(models.Transcript.id == id).first()
    if not transcript: raise HTTPException(status_code=404, detail="Transcript not found")
    facts = db.query(models.Fact).filter(models.Fact.transcript_id == id).all()
    conflicts = db.query(models.Conflict).filter(models.Conflict.transcript_id == id).all()
    summary = db.query(models.Summary).filter(models.Summary.transcript_id == id).first()
    return {"transcript": transcript, "facts": facts, "conflicts": conflicts, "summary": summary}
# --- End Veritas Deposition™ ---

@app.get("/leads/{lead_id}/conflict-check")
def run_conflict_check(lead_id: int, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.Lead).filter(models.Lead.id == lead_id)
    if current_firm:
        query = query.filter(models.Lead.firm_id == current_firm.id)
    lead = query.first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if not lead.full_name:
        return {"status": "Clear", "matches": [], "notes": "No name provided for check."}
    
    # Simple name-based search for potential conflicts
    # In a real app, this would check against a "Client" database and adverse parties.
    conflict_query = db.query(models.Lead).filter(
        models.Lead.full_name.ilike(f"%{lead.full_name}%"),
        models.Lead.id != lead_id
    )
    if current_firm:
        conflict_query = conflict_query.filter(models.Lead.firm_id == current_firm.id)
        
    potential_matches = conflict_query.all()
    
    status = "Clear"
    if len(potential_matches) > 0:
        status = "Potential Conflict"
    
    return {
        "status": status,
        "matches": [{"id": m.id, "name": m.full_name, "case": m.case_type} for m in potential_matches],
        "notes": f"Searched database for '{lead.full_name}'."
    }

@app.post("/demo/seed-voice")
def seed_voice_leads(db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    """Seed specialized leads that look like they came from Voice AI"""
    voice_lead = models.Lead(
        firm_id=current_firm.id if current_firm else None,
        full_name="Sarah Miller (Voice Intake)",
        email="smiller@example.com",
        phone="312-555-0982",
        case_type="Medical Malpractice",
        description="Incoming call from Sarah Miller regarding a surgical error at General Hospital. [VOICE AI INTAKE]",
        is_demo=1,
        source="Voice AI",
        qualification_score=88,
        status="Qualified",
        ai_summary="Caller reports surgical error during appendectomy. High medical merit."
    )
    db.add(voice_lead)
    db.flush()
    
    # Also seed a VoiceCall record
    voice_call = models.VoiceCall(
        firm_id=current_firm.id if current_firm else None,
        lead_id=voice_lead.id,
        vapi_call_id=f"vapi-{uuid.uuid4()}",
        phone_number="312-555-0982",
        recording_url="/assets/demo-recording.mp3",
        summary="Caller reports surgical error during appendectomy. High medical merit.",
        transcript="Assistant: Hello, how can I help you? Caller: I had surgery last week and they left a sponge inside me. Assistant: I'm so sorry to hear that...",
        duration_seconds=145,
        status="completed"
    )
    db.add(voice_call)
    db.commit()
    return {"status": "success", "lead_id": voice_lead.id}


@app.post("/demo/crm-sync")
async def demo_crm_sync(
    lead_id: int = Form(None),
    firm_slug: str = Form("lexiflow-tech"),
    db: Session = Depends(get_db),
):
    """
    Simulates a production-grade CRM sync for the NYC Bar demo.
    
    Takes an existing lead (or creates one from the Rodriguez scenario)
    and pushes the full Reasoning AI metadata bundle to Filevine and Clio:
    - Merit Score (92/100)
    - Settlement Value ($4.2M — NY no-cap)
    - 14-Hour Treatment Gap Contradiction Flag
    - 4 Negligence Markers
    - AI-Generated Cross-Examination Questions (3)
    
    Returns structured sync results matching what actual CRM integrations return.
    """
    import json as _json
    from integration_engine import IntegrationEngine, UniversalLeadMapper
    from crm.score_sync_engine import evaluate_score

    # Find or create the lead
    lead = None
    if lead_id:
        lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    
    if not lead:
        # Auto-create the Rodriguez demo lead
        firm = db.query(models.Firm).filter(models.Firm.slug == firm_slug).first()
        if not firm:
            firm = db.query(models.Firm).first()
        
        # Check if Rodriguez lead already exists
        lead = db.query(models.Lead).filter(
            models.Lead.full_name.ilike("%Rodriguez%"),
            models.Lead.firm_id == (firm.id if firm else None)
        ).first()
        
        if not lead:
            lead = models.Lead(
                firm_id=firm.id if firm else None,
                full_name="Elena Rodriguez",
                email="e.rodriguez@email.com",
                phone="(212) 555-0147",
                case_type="Medical Malpractice — Delayed Diagnosis",
                description="14-hour delay in antibiotic administration at Mount Sinai ER leading to septic shock and bilateral below-knee amputation.",
                qualification_score=87.0,
                status="High Priority",
                ai_summary="Definitive deviation from Standard of Care (Surviving Sepsis Campaign). Patient presented with 2/3 qSOFA criteria at triage. Antibiotics ordered at 19:15 but never administered until 10:15 next day — a 14-hour gap. Result: septic shock, bilateral foot necrosis, double amputation. Strong liability. NY has no damage cap.",
                case_value_estimate=4200000.0,
                source="AI Intake Demo",
                is_demo=1,
            )
            db.add(lead)
            db.flush()

    # Build the Reasoning AI metadata bundle
    reasoning_metadata = {
        "ai_qualification": {
            "priority_score": 87,
            "merit_score": 92,
            "negligence_markers": [
                {
                    "id": 1,
                    "marker": "14-Hour Treatment Gap",
                    "evidence": "MAR_Table_3, Nursing_Logs_P8",
                    "severity": "CRITICAL",
                    "description": "Antibiotics ordered at 19:15. First administration at 10:15 next day. 13.5 hours with zero documented care."
                },
                {
                    "id": 2,
                    "marker": "Sepsis Criteria Met at Triage — No Escalation",
                    "evidence": "ER_Triage_Page_1",
                    "severity": "HIGH",
                    "description": "qSOFA 2/3 at 18:30 (103.2°F, HR 115). No sepsis protocol escalation for 14 hours."
                },
                {
                    "id": 3,
                    "marker": "Ordered Antibiotics Never Administered",
                    "evidence": "Physician_Notes_P4 → MAR_Table_3",
                    "severity": "CRITICAL",
                    "description": "Vancomycin ordered at 19:15. MAR shows zero administration entries until 10:15."
                },
                {
                    "id": 4,
                    "marker": "No Vital Sign Monitoring During Gap",
                    "evidence": "Nursing_Logs_P8",
                    "severity": "HIGH",
                    "description": "No nursing notes, no vital sign re-checks for 13.5 hours during the critical overnight period."
                }
            ],
            "contradictions": [
                {
                    "testimony": "Dr. Alan Miller: 'I personally confirmed the start of the IV antibiotic protocol at 19:45.'",
                    "evidence": "MAR shows zero antibiotic dosage entries until 10:15 the following morning.",
                    "impeachment_question": "Doctor, you testified that you 'personally confirmed' the start of antibiotics at 19:45. Can you explain why the hospital's own electronic MAR shows no such administration occurred for the next 14 hours?",
                    "confidence": 0.97
                },
                {
                    "testimony": "Dr. Alan Miller: 'The patient's condition was stable throughout the evening shift.'",
                    "evidence": "qSOFA score of 2 at 18:30 — carries 10% in-hospital mortality risk.",
                    "impeachment_question": "You characterize a qSOFA score of 2 — which carries a 10% risk of in-hospital mortality — as 'stable'? Is that the standard definition of stability used at Mount Sinai?",
                    "confidence": 0.94
                }
            ],
            "cross_exam_questions": [
                "Does the hospital's Sepsis Protocol require the '3-Hour Bundle' for patients meeting 2/3 qSOFA criteria?",
                "If the '3-Hour Bundle' was not completed within 14 hours, would you agree that is a deviation from the hospital's internal safety guidelines?",
                "Who was the nurse assigned to Bed 4 between the hours of 20:00 and 08:00?"
            ],
            "settlement_analysis": {
                "jurisdiction": "New York",
                "estimated_value": 4200000,
                "value_range": {"low": 3500000, "high": 5200000},
                "damage_cap": "No cap — NY has no statutory limit on non-economic damages",
                "comparison_jurisdictions": {
                    "California (MICRA)": 353000,
                    "Texas (per defendant)": 750000,
                    "Florida": "No cap"
                },
                "injury_severity": "Catastrophic — Bilateral BKA amputation + permanent kidney damage"
            },
            "medical_chronology": {
                "source": "Discovery-Vault™ AI",
                "events": [
                    {"time": "May 10, 18:30", "event": "Admission — 103.2°F, HR 115, qSOFA 2/3", "ref": "ER_Triage_Page_1"},
                    {"time": "May 10, 19:15", "event": "Antibiotics ordered (Vancomycin)", "ref": "Physician_Notes_P4"},
                    {"time": "May 10 20:00 → May 11 09:30", "event": "⚠️ 14-HOUR GAP — No care documented", "ref": "MAR_Table_3, Nursing_Logs_P8", "flag": "CRITICAL"},
                    {"time": "May 11, 10:00", "event": "Code Blue — Septic shock (BP 70/40)", "ref": "Code_Sheet_P1"},
                    {"time": "May 12", "event": "Bilateral foot necrosis", "ref": "Surgical_Consult_P2"},
                    {"time": "May 15", "event": "Double BKA amputation", "ref": "Op_Report_May15"}
                ]
            }
        }
    }

    # Build CRM payloads using existing mapper
    mapper = UniversalLeadMapper()
    filevine_payload = mapper.map_lead(lead, "filevine")
    clio_payload = mapper.map_lead(lead, "clio")

    # Enhance payloads with Reasoning AI metadata
    filevine_payload["aiMetadata"] = reasoning_metadata
    filevine_payload["customFields"] = {
        "lexiflow_priority_score": 87,
        "lexiflow_merit_score": 92,
        "lexiflow_case_value": "$4,200,000",
        "lexiflow_negligence_markers": "4 detected — including 14-hour treatment gap",
        "lexiflow_contradictions": "2 high-confidence contradictions flagged",
        "lexiflow_cross_exam_questions": "3 AI-generated questions ready",
        "lexiflow_damage_cap_state": "NY — No cap",
    }

    clio_payload["ai_metadata"] = reasoning_metadata
    clio_payload["custom_fields"] = {
        "lead_score": "87/100 — High Priority",
        "merit_score": "92/100 — Strong Medical Merit",
        "case_value": "$4,200,000",
        "key_finding": "14-hour treatment gap — CRITICAL deviation"
    }

    # Evaluate score-based routing
    score_action = evaluate_score(87)

    # Simulate sync results as they would appear from live API calls
    sync_results = {
        "filevine": {
            "status": "success",
            "simulated": True,
            "action": "create_project",
            "project_name": "Rodriguez, Elena - Medical Malpractice — Delayed Diagnosis",
            "external_id": f"FV-PROJ-{lead.id:06d}",
            "reasoning_metadata_included": True,
            "custom_fields_set": list(filevine_payload["customFields"].keys()),
            "payload_preview": {k: v for k, v in filevine_payload.items() if k not in ["aiMetadata"]}
        },
        "clio": {
            "status": "success",
            "simulated": True,
            "action": "create_lead",
            "external_id": f"CLIO-LEAD-{lead.id:06d}",
            "reasoning_metadata_included": True,
            "custom_fields_set": list(clio_payload["custom_fields"].keys()),
        }
    }

    # Update lead record
    lead.sync_status = "Synced (Filevine + Clio)"
    lead.external_crm_id = sync_results["filevine"]["external_id"]
    db.commit()

    create_audit_log(
        db, "demo_crm_sync",
        lead.id,
        f"Filevine+Clio sync with full Reasoning AI metadata. Score: 87, Merit: 92, Value: $4.2M"
    )

    return {
        "status": "success",
        "demo_note": "This is a simulated CRM sync for demo purposes. Live sync requires configured CRM API keys.",
        "lead": {
            "id": lead.id,
            "name": lead.full_name,
            "score": lead.qualification_score,
            "merit_score": 92,
            "case_value": lead.case_value_estimate,
            "status": lead.status,
            "sync_status": lead.sync_status,
        },
        "reasoning_ai_bundle": {
            "merit_score": reasoning_metadata["ai_qualification"]["merit_score"],
            "negligence_markers_count": len(reasoning_metadata["ai_qualification"]["negligence_markers"]),
            "contradictions_count": len(reasoning_metadata["ai_qualification"]["contradictions"]),
            "cross_exam_questions_count": len(reasoning_metadata["ai_qualification"]["cross_exam_questions"]),
            "settlement_value": reasoning_metadata["ai_qualification"]["settlement_analysis"]["estimated_value"],
            "damage_cap_info": reasoning_metadata["ai_qualification"]["settlement_analysis"]["damage_cap"],
        },
        "sync_results": sync_results,
        "score_based_routing": {
            "action": score_action.action,
            "priority": score_action.priority,
            "sync_filevine": score_action.sync_filevine,
            "sync_clio": score_action.sync_clio,
            "notify_attorney": score_action.notify_attorney,
        }
    }


@app.get("/audit-logs")
def get_audit_logs(limit: int = 100, db: Session = Depends(get_db), current_firm: models.Firm = Depends(get_current_firm)):
    query = db.query(models.AuditLog)
    if current_firm:
        query = query.filter(models.AuditLog.firm_id == current_firm.id)
    logs = query.order_by(models.AuditLog.timestamp.desc()).limit(limit).all()
    return logs

# For local development and sandbox serving
if not os.getenv("VERCEL") and __name__ == "__main__":
    import uvicorn
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    # The root directory is the current directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    api_app = app
    app = FastAPI()
    
    @app.get("/cities/{city}")
    async def serve_city(city: str):
        city_file = os.path.join(root_dir, "cities", f"{city}.html")
        if os.path.exists(city_file):
            return FileResponse(city_file)
        raise HTTPException(status_code=404)

    @app.api_route("/meritscan", methods=["GET", "HEAD"])
    async def serve_meritscan():
        return FileResponse(os.path.join(root_dir, "meritscan.html"))

    # Blog URL normalization: clean URLs (no .html extension)
    @app.api_route("/blog/{slug:path}", methods=["GET", "HEAD"])
    async def serve_blog_slug(slug: str):
        # Try direct slug (no .html)
        blog_file = os.path.join(root_dir, "blog", f"{slug}.html")
        if os.path.exists(blog_file):
            return FileResponse(blog_file)
        # Try as directory index (blog/slug/index.html)
        blog_index = os.path.join(root_dir, "blog", slug, "index.html")
        if os.path.exists(blog_index):
            return FileResponse(blog_index)
        raise HTTPException(status_code=404)

    @app.api_route("/veritas/{path:path}", methods=["GET", "HEAD"])
    @app.api_route("/veritas", methods=["GET", "HEAD"])
    async def serve_veritas(path: str = None):
        # Serves the Veritas Deposition™ Evidence Intelligence SPA
        # Use the copy in the veritas/ directory at root for production consistency
        veritas_index = os.path.join(root_dir, "veritas/index.html")
        if not os.path.exists(veritas_index):
            # Fallback to the build directory if root copy missing
            veritas_index = os.path.join(root_dir, "veritas-deposition/frontend/dist/index.html")
        return FileResponse(veritas_index)

    @app.api_route("/depolens", methods=["GET", "HEAD"])
    async def serve_depolens():
        # Alias for Veritas Deposition™
        return await serve_veritas()

    @app.api_route("/veritas-app", methods=["GET", "HEAD"])
    async def serve_veritas_legacy():
        return await serve_veritas()

    # Clean URL support: /page → /page.html
    # List of pages that should be accessible without .html extension
    CLEAN_URL_PAGES = [
        "pricing", "signup", "login", "dashboard", "ai-legal-intake-software",
        "ai-medical-chronologies", "voice-ai-receptionist", "compliance-shield",
        "discovery-vault", "settlement-predictor", "roi-calculator",
        "meritscan", "privacy", "terms", "soc2", "security",
        "ai-intake-agent", "auto-document-drafter", "integrations",
        "witness-testimony-analysis", "personal-injury-software",
        "medical-chronology-software", "medical-chronology-template",
        "medical-chronology-sample", "medical-record-review-checklist",
        "case-studies", "roi-report-template", "veritas-app",
        "san-francisco-medical-malpractice-intake", "strategist",
        "veritas-deposition",
    ]
    for page in CLEAN_URL_PAGES:
        html_path = os.path.join(root_dir, f"{page}.html")
        if os.path.exists(html_path):
            @app.api_route(f"/{page}", methods=["GET", "HEAD"])
            async def _serve_clean_url(page=page):
                return FileResponse(os.path.join(root_dir, f"{page}.html"))

    # Resources pages: /resources/medical-chronology-template → /resources/medical-chronology-template.html
    RESOURCE_PAGES = ["medical-chronology-template", "medical-chronology-sample", "medical-record-review-checklist"]
    for rp in RESOURCE_PAGES:
        rp_path = os.path.join(root_dir, "resources", f"{rp}.html")
        if os.path.exists(rp_path):
            @app.api_route(f"/resources/{rp}", methods=["GET", "HEAD"])
            async def _serve_resource(rp=rp):
                return FileResponse(os.path.join(root_dir, "resources", f"{rp}.html"))

    app.mount("/api", api_app)
    app.mount("/", StaticFiles(directory=root_dir, html=True), name="static")
    
    port = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)

