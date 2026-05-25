from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
import uuid
import httpx
import json

from . import models, database, ai_engine, esign_engine, integration_engine
from .database import engine, get_db

def create_audit_log(db: Session, action: str, lead_id: int = None, details: str = None):
    log = models.AuditLog(lead_id=lead_id, action=action, details=details)
    db.add(log)
    db.commit()

app = FastAPI(title="LexiFlow API")

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": "vercel" if os.getenv("VERCEL") else "local"}

# CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def start_chat(db: Session = Depends(get_db)):
    lead = models.Lead()
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return {"lead_id": lead.id}

@app.post("/demo-request")
def demo_request(name: str = Form(...), email: str = Form(...), firm: str = Form(None), db: Session = Depends(get_db)):
    demo_req = models.DemoRequest(name=name, email=email, firm=firm)
    db.add(demo_req)
    db.commit()
    create_audit_log(db, "demo_request", details=f"Name: {name}, Email: {email}, Firm: {firm}")
    return {"status": "success", "message": "Demo request received"}

@app.post("/demo/seed")
def seed_demo_leads(firm: str = Form("General"), db: Session = Depends(get_db)):
    # Delete existing demo leads to refresh for the specific firm if requested
    db.query(models.Lead).filter(models.Lead.is_demo == 1).delete()
    
    demo_leads = []
    
    if firm == "Smith LaCien":
        demo_leads = [
            models.Lead(
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
                full_name="Aviation Incident: Pilot Error",
                email="survivor@aviation.com",
                phone="773-555-1234",
                case_type="Aviation Accident",
                description="Engine failure during takeoff from Midway. Minor injuries but severe emotional distress.",
                qualification_score=82.0,
                status="Qualified",
                ai_summary="Aviation litigation lead. Potential for punitive damages if maintenance records show pattern of neglect.",
                is_demo=1
            ),
            models.Lead(
                full_name="Truck Collision: Route 66",
                email="driver.hit@gmail.com",
                phone="312-555-4444",
                case_type="Personal Injury - Trucking",
                description="Jackknifed semi-truck on I-55. Client sustained multiple fractures and head trauma.",
                qualification_score=94.2,
                status="High Priority",
                ai_summary="High-stakes trucking accident. Logbook violations suspected. Strong liability against the carrier.",
                is_demo=1
            )
        ]
    elif firm == "Clifford Law":
        demo_leads = [
            models.Lead(
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
    elif firm == "Levin & Perconti":
        demo_leads = [
            models.Lead(
                full_name="Nursing Home Abuse: Maria G.",
                email="daughter@family.org",
                phone="847-555-6789",
                case_type="Nursing Home Abuse",
                description="Unexplained bruising and rapid weight loss at Sunset Care facility.",
                qualification_score=89.5,
                status="High Priority",
                ai_summary="Serious elder abuse allegation. Levin & Perconti's niche. Needs immediate intervention.",
                is_demo=1
            ),
            models.Lead(
                full_name="Wrongful Death: James P.",
                email="estate.admin@legalservices.net",
                phone="708-555-3333",
                case_type="Medical Malpractice / Wrongful Death",
                description="Failure to diagnose sepsis in a nursing home resident, leading to death within 48 hours.",
                qualification_score=96.8,
                status="High Priority",
                ai_summary="Devastating wrongful death lead. Clear failure in standard of care. Perfect for L&P's senior litigation team.",
                is_demo=1
            )
        ]
    else:
        demo_leads = [
            models.Lead(
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
        msg1 = models.Message(lead_id=lead.id, role="assistant", content="Hello! I'm Lexi, your AI legal assistant. I'm here to help you through this difficult time.")
        msg2 = models.Message(lead_id=lead.id, role="user", content=lead.description)
        msg3 = models.Message(lead_id=lead.id, role="assistant", content="I've recorded all the details. An attorney will review your case immediately.")
        db.add_all([msg1, msg2, msg3])

    db.commit()
    return {"status": "success", "message": f"Demo leads seeded for {firm}"}

@app.get("/demo/firms")
def get_demo_firms():
    return ["General", "Smith LaCien", "Clifford Law", "Levin & Perconti"]

@app.post("/sync/{system}/{lead_id}")
async def universal_sync(system: str, lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
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
    
    # Get AI response
    ai_content = ai_engine.get_ai_response(history)
    
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
    kb_entries = db.query(models.KnowledgeBase).filter(models.KnowledgeBase.is_active == 1).all()
    kb_context = "\n".join([f"KB - {k.title}: {k.content}" for k in kb_entries])
    
    score, status, summary, client_info, case_value = ai_engine.qualify_lead(full_transcript, context=kb_context)
    
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
            
    db.commit()
    
    create_audit_log(db, "lead_qualified", lead_id, f"Score: {score}, Status: {status}")
    
    return {"status": status, "score": score}

@app.get("/leads", response_model=List[dict])
def get_leads(demo_mode: bool = False, db: Session = Depends(get_db)):
    query = db.query(models.Lead)
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
def get_lead_detail(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
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
def create_form(name: str = Form(...), branding_logo: str = Form(None), branding_colors: str = Form(None), questions_json: str = Form(...), db: Session = Depends(get_db)):
    form = models.Form(name=name, branding_logo=branding_logo, branding_colors=branding_colors)
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
def get_forms(db: Session = Depends(get_db)):
    forms = db.query(models.Form).all()
    return forms

@app.get("/forms/{form_id}")
def get_form(form_id: int, db: Session = Depends(get_db)):
    form = db.query(models.Form).filter(models.Form.id == form_id).first()
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
    answers = json.loads(answers_json) # dict of question_id: answer
    
    # Create a lead
    name = answers.get('name') or answers.get('full_name')
    if not name:
        # Try to find a question that might be the name
        name = "Form Lead"
    
    lead = models.Lead(full_name=name)
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
            
    score, status, summary = ai_engine.qualify_lead(context, context=form.qualification_rules)
    lead.qualification_score = score
    lead.status = status
    lead.ai_summary = summary
    
    db.commit()
    return {"status": "success", "lead_id": lead.id}

@app.post("/reception/webhook")
async def reception_webhook(
    name: str = Form(...), 
    email: str = Form(None), 
    phone: str = Form(None), 
    notes: str = Form(None), 
    source: str = Form("Receptionist"),
    db: Session = Depends(get_db)
):
    """
    Endpoint for virtual receptionists (e.g., Ruby, Smith.ai) to push lead info.
    """
    lead = models.Lead(
        full_name=name, 
        email=email, 
        phone=phone, 
        description=notes, 
        source=source
    )
    db.add(lead)
    db.flush()
    
    # AI Qualification
    kb_entries = db.query(models.KnowledgeBase).filter(models.KnowledgeBase.is_active == 1).all()
    kb_context = "\n".join([f"KB - {k.title}: {k.content}" for k in kb_entries])
    
    score, status, summary = ai_engine.qualify_lead(f"Receptionist Notes: {notes}", context=kb_context)
    lead.qualification_score = score
    lead.status = status
    lead.ai_summary = summary
    
    db.commit()
    
    create_audit_log(db, "reception_sync", lead.id, f"Source: {source}")
    
    return {"status": "success", "lead_id": lead.id}

@app.get("/knowledge-base")
def get_kb(db: Session = Depends(get_db)):
    return db.query(models.KnowledgeBase).all()

@app.post("/knowledge-base")
def add_kb(title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    kb = models.KnowledgeBase(title=title, content=content)
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb

@app.delete("/knowledge-base/{kb_id}")
def delete_kb(kb_id: int, db: Session = Depends(get_db)):
    kb = db.query(models.KnowledgeBase).filter(models.KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(kb)
    db.commit()
    return {"status": "success"}

@app.get("/billing/invoices")
def get_invoices(db: Session = Depends(get_db)):
    invoices = db.query(models.Invoice).all()
    return invoices

@app.post("/billing/invoices")
def create_invoice(lead_id: int = Form(...), amount: float = Form(...), currency: str = Form("USD"), description: str = Form(None), db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    invoice = models.Invoice(lead_id=lead_id, amount=amount, currency=currency, description=description)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    # Simulate LawPay integration by generating an external ID
    invoice.external_id = f"lp_{uuid.uuid4().hex[:8]}"
    db.commit()
    
    create_audit_log(db, "invoice_created", lead_id, f"Amount: {amount} {currency}")
    
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
def send_esign_request(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
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
def get_esign_status(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
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
def simulate_esign_signed(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead.esign_status = "Signed"
    db.commit()
    
    create_audit_log(db, "esign_signed", lead_id, "Simulated status update")
    
    return {"status": "success", "message": "Lead status updated to Signed"}

@app.get("/leads/{lead_id}/export/clio")
def export_lead_clio_csv(lead_id: int, db: Session = Depends(get_db)):
    """Export lead in Clio-compatible CSV format"""
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
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
        lead.source or "LexiFlow AI",
        lead.status or "New"
    ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=clio_lead_{lead_id}.csv"}
    )

# GDPR & Compliance Endpoints
@app.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    """Right to be Forgotten - GDPR Compliance"""
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
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
def export_lead_data(lead_id: int, db: Session = Depends(get_db)):
    """Data Portability - GDPR Compliance"""
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
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
def generate_demand_draft(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    messages = db.query(models.Message).filter(models.Message.lead_id == lead_id).order_by(models.Message.timestamp.asc()).all()
    transcript = "\n".join([f"{m.role}: {m.content}" for m in messages])
    
    draft = ai_engine.draft_demand_letter(transcript)
    lead.demand_letter_draft = draft
    db.commit()
    
    create_audit_log(db, "demand_draft_generated", lead_id)
    
    return {"draft": draft}

@app.get("/leads/{lead_id}/medical-chronology")
def get_medical_chronology(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    messages = db.query(models.Message).filter(models.Message.lead_id == lead_id).order_by(models.Message.timestamp.asc()).all()
    transcript = "\n".join([f"{m.role}: {m.content}" for m in messages])
    
    chronology = ai_engine.generate_medical_chronology(transcript)
    
    create_audit_log(db, "medical_chronology_generated", lead_id)
    
    return {"chronology": chronology}

@app.get("/leads/{lead_id}/conflict-check")
def run_conflict_check(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if not lead.full_name:
        return {"status": "Clear", "matches": [], "notes": "No name provided for check."}
    
    # Simple name-based search for potential conflicts
    # In a real app, this would check against a "Client" database and adverse parties.
    potential_matches = db.query(models.Lead).filter(
        models.Lead.full_name.ilike(f"%{lead.full_name}%"),
        models.Lead.id != lead_id
    ).all()
    
    status = "Clear"
    if len(potential_matches) > 0:
        status = "Potential Conflict"
    
    return {
        "status": status,
        "matches": [{"id": m.id, "name": m.full_name, "case": m.case_type} for m in potential_matches],
        "notes": f"Searched database for '{lead.full_name}'."
    }

@app.post("/demo/seed-voice")
def seed_voice_leads(db: Session = Depends(get_db)):
    """Seed specialized leads that look like they came from Voice AI"""
    voice_lead = models.Lead(
        full_name="Sarah Miller (Voice Intake)",
        email="smiller@example.com",
        phone="312-555-0982",
        case_type="Medical Malpractice",
        description="Incoming call from Sarah Miller regarding a surgical error at General Hospital. [VOICE AI INTAKE]",
        is_demo=1,
        status="High Priority",
        score=92.0,
        case_value_estimate=150000.0,
        source="Voice AI Receptionist"
    )
    db.add(voice_lead)
    db.commit()
    db.refresh(voice_lead)
    
    # Add simulated phone transcript
    transcript = [
        ("ai", "Hello, thank you for calling LexiFlow Legal. This is Lexi, how can I help you today?"),
        ("user", "Yes, I'm calling about my surgery last month. Something went very wrong."),
        ("ai", "I'm so sorry to hear that. I'm here to gather some details for our attorneys. Can you tell me which hospital this was at?"),
        ("user", "It was at Chicago General. I went in for a routine gallbladder removal but they punctured my lung."),
        ("ai", "That sounds extremely serious. When exactly did this happen?"),
        ("user", "On April 12th. I've been in and out of the ICU since then."),
        ("ai", "I understand. I'm going to flag this for immediate review by our senior partners. Could you provide your email address so we can send you some initial documents?")
    ]
    
    for role, content in transcript:
        msg = models.Message(lead_id=voice_lead.id, role=role, content=content)
        db.add(msg)
    
    db.commit()
    return {"status": "success", "lead_id": voice_lead.id}

@app.get("/audit-logs")
def get_audit_logs(limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).limit(limit).all()
    return logs

# For local development and sandbox serving
if not os.getenv("VERCEL"):
    from fastapi.staticfiles import StaticFiles
    # The root directory is the parent of the backend directory
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    api_app = app
    app = FastAPI()
    app.mount("/api", api_app)
    app.mount("/", StaticFiles(directory=root_dir, html=True), name="static")

