import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY")
base_url = os.getenv("AI_BASE_URL")
model_name = os.getenv("AI_MODEL")

# Optional Gemini support
gemini_key = os.getenv("GEMINI_API_KEY")
try:
    if gemini_key:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
except ImportError:
    genai = None

# Auto-detect Groq and configure defaults if not provided
if api_key and api_key.startswith("gsk_"):
    if not base_url:
        base_url = "https://api.groq.com/openai/v1"
    if not model_name:
        model_name = "llama-3.1-70b-versatile"
elif not model_name:
    model_name = "gpt-4o"

# Initialize client only if API key is provided
client = None
if api_key:
    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")


# ===================== USAGE METERING INTEGRATION =====================

from usage_tracker import usage_tracker, UsageLimitExceeded
from database import SessionLocal as _usage_db_session


def check_document_processing_limit(firm_id=None) -> dict:
    """
    Check if a firm has remaining document processing quota.
    If firm_id is None, returns unlimited (no check).
    
    Returns {'ok': True} or raises UsageLimitExceeded with billing info.
    For non-DB mode, always returns unlimited.
    """
    if firm_id is None:
        return {"ok": True, "note": "no firm_id — unlimited"}
    
    try:
        db = _usage_db_session()
        try:
            result = usage_tracker.check_usage_limit(firm_id, db=db)
            if not result.get("can_process", True):
                raise UsageLimitExceeded(
                    firm_id=firm_id,
                    tier=result.get("tier", "standard"),
                    current_count=result.get("current_usage", 0),
                    limit=result.get("monthly_limit", 0),
                    billing_period=result.get("billing_period", "")
                )
            return {"ok": True, "remaining": result.get("remaining", 0)}
        finally:
            db.close()
    except UsageLimitExceeded:
        raise
    except Exception as e:
        # If DB isn't available (e.g. demo mode), allow processing
        logger = __import__('logging').getLogger(__name__)
        logger.warning(f"Usage check skipped (DB unavailable): {e}")
        return {"ok": True, "note": f"check skipped: {e}"}


def record_document_processing(firm_id=None, doc_type="document_review",
                                doc_name="", pages=0, tokens=0, db=None):
    """Record a document processing event for billing."""
    if firm_id is None:
        return {"status": "skipped", "note": "no firm_id"}
    try:
        s = db or (_usage_db_session() if not db else None)
        return usage_tracker.record_usage(
            firm_id=firm_id, doc_type=doc_type, doc_name=doc_name,
            pages=pages, tokens=tokens, db=s
        )
    except Exception as e:
        logger = __import__('logging').getLogger(__name__)
        logger.warning(f"Usage recording skipped: {e}")
        return {"status": "skipped", "note": str(e)}


# ===================== END USAGE METERING INTEGRATION =====================

def get_ai_response(messages):
    """
    Unified AI response handler with fallback to Mock Mode.
    """
    if not client:
        return "I'm Lexi, and I'm currently running in demo mode. I can help summarize your case and collect your contact information. What happened during your incident?"

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI Engine Error: {e}")
        return "I'm having a brief connection issue with my brain, but I'm still listening! Could you tell me more about the injuries involved?"

import base64

def analyze_document_image(file_path, filename, firm_id=None):
    """
    Use AI Vision to extract key legal data from a document image.
    Checks usage limits if firm_id is provided.
    """
    check_document_processing_limit(firm_id)

    if not client:
        return {"document_type": "Unknown", "extracted_fields": {"note": "AI Client not configured"}}

    with open(file_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    extension = filename.split(".")[-1].lower()
    mime_type = "image/jpeg"
    if extension == "png": mime_type = "image/png"
    
    prompt = f"""
    Analyze this document image named '{filename}'.
    Identify the document type (e.g., Driver's License, Insurance Card, Police Report).
    Extract key information such as names, dates, policy numbers, or ID numbers.
    
    Return ONLY a JSON object with:
    {{
        "document_type": "...",
        "extracted_fields": {{
            "field_name": "value",
            ...
        }},
        "summary": "..."
    }}
    """

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return {"error": str(e)}

def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file using PyMuPDF.
    Wrapped in try/except for Vercel stability.
    """
    text = ""
    try:
        import fitz
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"PDF Extraction Warning: {e}")
        text = "[System Note: PDF extraction failed or not supported in this environment. Manual review required.]"
    return text

def get_ai_response(messages, context=None):
    """
    Get a response from the AI for the intake chatbot.
    """
    def get_mock_response(msgs):
        if not msgs:
            return "Hello! I'm LexiFlow, your legal intake assistant. How can I help you today?"
        
        last_msg = msgs[-1]["content"].lower()
        if "hello" in last_msg or "hi" in last_msg:
            return "Hello! I'm LexiFlow, your legal intake assistant. How can I help you today? Are you looking for a legal intake solution for your firm, or do you have a specific case you'd like me to evaluate?"
        elif "injury" in last_msg or "accident" in last_msg or "hurt" in last_msg:
            return "I'm sorry to hear that you've been injured. To help our attorneys evaluate your claim, could you tell me approximately when this happened and if anyone else was involved?"
        elif "demo" in last_msg or "how it works" in last_msg:
            return "LexiFlow uses Reasoning AI to qualify leads 24/7. It understands the nuances of legal claims better than old-fashioned forms. You can try our Live Demo or click 'Request Demo' to talk to our team!"
        else:
            return "Thank you for that information. Could you please provide your full name and the best phone number for an attorney to reach you at?"

    if not client:
        return get_mock_response(messages)

    kb_info = f"\n\nFirm-Specific Knowledge Base:\n{context}" if context else ""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are Lexi, the LexiFlow Technologies Inc Assistant. You are professional, empathetic, and expert in legal intake. Your goal is to help potential clients understand how LexiFlow can help their firm, answer general questions about the platform, or begin a case intake.\n\nKey LexiFlow Facts:\n- 391% conversion boost for law firms.\n- Recaptures $12,000+ in billable hours per month.\n- 24/7 availability for lead capture and qualification.\n- Uses Reasoning AI (LLMs) instead of legacy Decision Trees to understand case nuances.\n- Direct sync to Clio, MyCase, and Filevine.\n- LexiFlow is NOT a law firm and does NOT provide legal advice.\n- You are multilingual and can converse fluently in Spanish, French, and other languages if the user initiates.\n\nIf a user wants to start an intake, guide them through it. If they want a demo, suggest clicking the 'Request Demo' button." + kb_info},
                *messages
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI API Error: {str(e)}")
        # Fallback to mock on any API error (including invalid key)
        return get_mock_response(messages)

def qualify_lead(transcript, context=None):
    """
    Qualify the lead based on the chat transcript and optional context.
    """
    def get_mock_qualification():
        return 75.0, "High Priority", "Potential personal injury case with clear incident date and contact info. [MOCK]", {}, 50000.0

    if not client:
        return get_mock_qualification()

    context_str = f"\nAdditional Context/Rules:\n{context}" if context else ""
    
    prompt = f"""
    Analyze the following legal intake transcript and provide:
    1. A qualification score (0-100).
    2. A status (High Priority, Requires Review, Disqualified).
    3. A brief summary of the case.
    4. Extracted client info (Full Name, Email, Phone).
    5. A potential settlement value estimate (USD float). Be conservative.

    {context_str}

    Transcript:
    {transcript}

    Return ONLY a JSON object with:
    {{
        "score": 0-100,
        "status": "...",
        "summary": "...",
        "case_value": 0.0,
        "client_info": {{
            "full_name": "...",
            "email": "...",
            "phone": "..."
        }}
    }}
    """

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert legal case evaluator. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        import json
        data = json.loads(response.choices[0].message.content)
        score = float(data.get("score", 0))
        status = data.get("status", "Requires Review")
        summary = data.get("summary", "")
        client_info = data.get("client_info", {})
        case_value = float(data.get("case_value", 0.0))
        
        return score, status, summary, client_info, case_value
    except Exception as e:
        print(f"Error qualifying lead: {e}")
        return get_mock_qualification()

def draft_demand_letter(transcript, firm_name="LexiFlow Legal"):
    """
    Draft a professional demand letter based on the intake facts.
    """
    if not client:
        return "Demand Letter Draft: [MOCK] We hereby demand settlement for the injuries sustained by our client in the accident described in the transcript."

    prompt = f"""
    Based on the following legal intake transcript, draft a professional, formal Demand Letter to an insurance company.
    Use '{firm_name}' as the law firm.
    Include sections for: Facts of the Accident, Injuries Sustained, and a Formal Demand for Settlement.
    
    Transcript:
    {transcript}
    """

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a professional personal injury attorney drafting a formal demand letter."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error drafting demand letter: {str(e)}"

def analyze_document_text(text, filename, firm_id=None):
    """
    Use AI to extract key legal data from document text.
    Checks usage limits if firm_id is provided.
    """
    check_document_processing_limit(firm_id)

    if not client:
        return {"document_type": "Unknown", "extracted_fields": {"note": "AI Client not configured"}}

    prompt = f"""
    Analyze the following text extracted from a document named '{filename}'.
    Identify the document type (e.g., Driver's License, Insurance Card, Police Report, Medical Record, NTSB Report, Technical Manual).
    Extract key information such as names, dates, policy numbers, ID numbers, or critical safety/incident facts.
    If it's a technical or medical report, provide a structured summary of the most legally significant findings.
    
    Text:
    {text[:4000]} 

    Return ONLY a JSON object with:
    {{
        "document_type": "...",
        "extracted_fields": {{
            "field_name": "value",
            ...
        }},
        "summary": "..."
    }}
    """

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a legal document analyzer. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error analyzing document: {e}")
        return {"error": str(e)}

def generate_medical_chronology(transcript, firm_id=None):
    """
    Generate a structured medical chronology from a legal intake transcript.
    Checks usage limits if firm_id is provided.
    """
    check_document_processing_limit(firm_id)

    if not client:
        return [
            {"date": "2024-05-10", "event": "Motor Vehicle Accident", "details": "High-impact rear-end collision reported by client. [MOCK]"},
            {"date": "2024-05-10", "event": "ER Visit", "details": "Client transported to General Hospital via EMS. Complaints of neck and back pain. [MOCK]"},
            {"date": "2024-05-12", "event": "Follow-up", "details": "Visit with primary care physician. Referred to MRI and Physical Therapy. [MOCK]"}
        ]

    prompt = f"""
    Analyze the following legal intake transcript and extract all medical-related events into a chronological timeline.
    For each event, provide:
    1. The Date (or approximate time).
    2. The Event/Provider Name.
    3. Brief Details of the treatment or symptoms.

    Transcript:
    {transcript}

    Return ONLY a JSON array of objects:
    [
        {{"date": "...", "event": "...", "details": "..."}},
        ...
    ]
    """

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a medical-legal consultant. Extract chronologies into JSON arrays."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" } if "gpt-4o" in model_name or "llama-3.1" in model_name else None
        )
        data = json.loads(response.choices[0].message.content)
        # Handle cases where LLM returns {"chronology": [...]} instead of just [...]
        if isinstance(data, dict) and "chronology" in data:
            return data["chronology"]
        if isinstance(data, dict) and len(data.keys()) == 1:
             key = list(data.keys())[0]
             if isinstance(data[key], list):
                 return data[key]
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Error generating chronology: {e}")
        return []

def generate_qualification_rules(firm_name, criteria_text):
    """
    Generate detailed qualification rules for a law firm based on provided text.
    """
    if not client:
        return f"Standard personal injury qualification rules for {firm_name}."

    prompt = f"""
    Create a detailed set of case qualification rules for the law firm '{firm_name}'.
    Use the following information as your primary guide:
    {criteria_text}
    
    Format the rules as a series of clear, actionable bullet points in Markdown.
    The goal is for another AI to use these rules to score and status incoming leads.
    
    Include:
    - High-value case indicators (e.g., specific injuries, liability clarity, insurance coverage).
    - Automatic disqualifiers (e.g., statute of limitations expired, conflict of interest, wrong practice area).
    - Differentiators specific to {firm_name}'s practice.
    
    Be specific and professional.
    """

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a senior law firm intake consultant and legal strategist. Your task is to extract qualification criteria from raw data and turn them into clear instructions for an intake AI."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating rules: {e}")
        # Robust fallback using basic extraction
        high_value_keywords = [
            "aviation", "birth injury", "brain injury", "wrongful death", 
            "medical malpractice", "truck accident", "mass tort", 
            "spinal cord injury", "cerebral palsy", "hypoxia"
        ]
        found = [k.title() for k in high_value_keywords if k in criteria_text.lower()]
        
        rules = f"### Qualification Rules for {firm_name}\n\n"
        rules += "#### High-Value Case Indicators\n"
        if found:
            for f in found:
                rules += f"- Case involves **{f}**.\n"
        else:
            rules += "- Clear liability and significant damages.\n"
            rules += "- Practice area alignment (Personal Injury).\n"
            
        rules += "\n#### Disqualifiers\n"
        rules += "- Conflict of interest.\n"
        rules += "- Statute of limitations expired.\n"
        rules += "- Incident outside firm's geographic jurisdiction.\n"
        
        rules += "\n#### Practice Focus\n"
        rules += f"- This set of rules was automatically generated via LexiFlow heuristic analysis for {firm_name}."
        
        return rules

def analyze_transcript(text):
    """
    Main entry point for Veritas Deposition™ AI analysis.
    Uses mock if no client.
    """
    if not client:
        witnesses = ["John Smith", "Jane Doe"]
        if "SMITH" in text.upper(): witnesses[0] = "John Smith"
        
        return {
            "chronology": [
                {"Witness Name": witnesses[0], "Date and Time": "May 26, 2026, 10:00 PM", "Event Description": "Claimed to be at home sleeping during the incident.", "Page Reference": 4},
                {"Witness Name": witnesses[1], "Date and Time": "May 26, 2026, 10:00 PM", "Event Description": "Observed John Smith at 'The Rusty Anchor' bar.", "Page Reference": 12}
            ],
            "conflicts": [
                {
                    "Witness A": witnesses[0],
                    "Witness B": witnesses[1],
                    "Conflict Description": "Contradiction regarding location at time of incident.",
                    "Reasoning": f"{witnesses[0]} claims he was at home, while {witnesses[1]} testifies seeing him at a bar.",
                    "Severity": "High"
                }
            ],
            "summary": {
                "admissions": "John Smith admitted he never goes to that bar, creating a firm denial that can be tested.\nJane Doe admitted she was at the bar for several hours.",
                "risks": "The direct contradiction between the two primary witnesses creates a significant credibility issue for the defense.",
                "executive_summary": "The deposition reveals a critical conflict regarding the whereabouts of the defendant. (LexiFlow Suite Analysis)"
            }
        }

    # Real AI logic (Simplified version of Veritas Deposition™ logic)
    prompt = f"""
    Analyze the following deposition transcript.
    1. Extract a structured Fact Chronology.
    2. Identify conflicts between witnesses.
    3. Provide an Executive Summary.

    Return JSON with keys: "chronology", "conflicts", "summary".
    
    Transcript:
    {text[:10000]}
    """
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return {"error": str(e)}

def generate_merit_report(text):
    """
    Generate a full merit review report from medical record text.
    """
    if not client:
        return {
            "executive_summary": "[DEMO MODE] Case shows significant merit due to delayed diagnosis of sepsis. Patient presented with classic symptoms that were ignored for 14 hours.",
            "chronology": "[DEMO MODE] 2026-05-10 14:00: Admitted with high fever. 2026-05-11 04:00: Vital signs unstable. 2026-05-11 06:00: Sepsis confirmed.",
            "negligence_markers": "[DEMO MODE] 1. Failure to monitor vitals at required intervals. 2. 6-hour delay in ordering blood cultures.",
            "standard_of_care_analysis": "[DEMO MODE] Standard of Care requires SIRS screening within 1 hour of presentation. The facility failed this benchmark by 13 hours."
        }
    
    prompt = f"Analyze the following medical record text and generate a comprehensive merit review report for a potential medical malpractice claim. Structure the report with the following sections: 1. Executive Summary, 2. Chronology, 3. Negligence Markers, 4. Standard of Care Analysis. Return the response as a JSON object with keys: executive_summary, chronology, negligence_markers, standard_of_care_analysis. Medical Record Text: {text[:4000]}"
    
    messages = [
        {"role": "system", "content": "You are a senior medical-legal expert consultant. Always return JSON."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response_text = get_ai_response(messages)
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return {
            "executive_summary": response_text,
            "chronology": "Extracted from summary",
            "negligence_markers": "Extracted from summary",
            "standard_of_care_analysis": "Extracted from summary"
        }
    except Exception as e:
        return {"error": str(e)}


# =========================================================================
# LexiFlow Strategist™ — AI Endpoints
# =========================================================================

def generate_life_care_plan(injury: str, age: int, state: str) -> dict:
    """
    Generate a comprehensive life care plan for catastrophic injury cases.
    Uses life expectancy tables and standard cost data.
    """
    if not client:
        return {
            "summary": f"Life care plan for {injury} (age {age}, {state})",
            "annual_costs": {
                "physician_visits": 8500,
                "physical_therapy": 12000,
                "home_health_aide": 72000,
                "medications": 14400,
                "medical_equipment": 5600,
                "transportation": 3600,
                "home_modifications": 18000,
                "case_management": 6000
            },
            "annual_total": 140100,
            "life_expectancy_years": 38,
            "lifetime_total": 5323800,
            "cost_categories": [
                {"category": "Medical Care", "annual": 45000, "lifetime": 1710000, "source": "U.S. Bureau of Labor Statistics"},
                {"category": "Personal Care", "annual": 72000, "lifetime": 2736000, "source": "Genworth Cost of Care Survey 2025"},
                {"category": "Therapies", "annual": 12000, "lifetime": 456000, "source": "Medicare Fee Schedule 2025"},
                {"category": "Equipment & Modifications", "annual": 11000, "lifetime": 418000, "source": "NMEDA Guidelines"}
            ],
            "note": "MOCK DATA — Configure Groq API key for AI-generated estimates."
        }

    prompt = f"""
    Generate a detailed life care plan for a catastrophic injury case in legal context.
    
    Patient details:
    - Injury: {injury}
    - Current Age: {age}
    - State of Residence: {state}
    
    Include:
    1. Annual cost breakdown by category (physician visits, PT/OT, home health aide, medications, equipment, transportation, home modifications, case management)
    2. Life expectancy estimate based on injury
    3. Lifetime total cost
    4. Medical source references for each cost category
    
    Return ONLY valid JSON with keys: summary, annual_costs (object), annual_total (number), life_expectancy_years (number), lifetime_total (number), cost_categories (array of objects with category, annual, lifetime, source).
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a board-certified physiatrist and life care planning expert with 20+ years of experience. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e), "annual_costs": {}, "annual_total": 0, "life_expectancy_years": 0, "lifetime_total": 0, "cost_categories": []}


def generate_opposing_counsel_profile(attorney_name: str, firm: str, practice_area: str) -> dict:
    """
    Profile opposing counsel based on name, firm, and practice area.
    """
    if not client:
        return {
            "attorney": attorney_name,
            "firm": firm,
            "practice_area": practice_area,
            "win_rate_estimate": "55-65%",
            "settlement_rate": "70%",
            "litigation_style": "Aggressive — known for extensive discovery demands and frequent motion practice. Prefers trial over settlement in high-value cases.",
            "notable_cases": [
                {"case": f"{firm} v. Defendant (2023)", "outcome": "$2.3M verdict — medical malpractice"},
                {"case": f"{firm} v. Healthcare Co. (2022)", "outcome": "Confidential settlement — product liability"}
            ],
            "strategy_tips": [
                "Prepare for aggressive discovery — expect extensive document requests",
                "Consider early mediation — this attorney responds well to well-prepared Daubert motions",
                "Focus on damages evidence early — they settle when liability is uncertain but fight on clear liability"
            ],
            "note": "MOCK DATA — Configure Groq API key for AI-generated profiles."
        }
    
    prompt = f"""
    Generate a detailed opposing counsel profile for litigation preparation.
    
    Attorney Details:
    - Name: {attorney_name}
    - Firm: {firm}
    - Practice Area: {practice_area}
    
    Include:
    1. Win rate estimate (range)
    2. Settlement rate (percentage)
    3. Litigation style description (detailed)
    4. 2-3 notable cases with outcomes
    5. 3 strategy tips for opposing this attorney
    
    Return ONLY valid JSON with keys: attorney (string), firm (string), practice_area (string), win_rate_estimate (string), settlement_rate (string), litigation_style (string), notable_cases (array of {{case, outcome}}), strategy_tips (array of strings).
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a senior litigation consultant who has analyzed thousands of attorneys. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e), "notable_cases": [], "strategy_tips": []}


def generate_sol_guardian(case_type: str, incident_date: str, state: str) -> dict:
    """
    Generate Statute of Limitations analysis with deadlines and filing checklist.
    """
    if not client:
        return {
            "case_type": case_type,
            "incident_date": incident_date,
            "state": state,
            "sol_deadline": "2028-05-10",
            "days_remaining": 655,
            "tolling_exceptions": [
                "Discovery Rule — statute begins when injury discovered (applies to medical malpractice with foreign object)",
                "Minority Tolling — if plaintiff was under 18 at time of incident, statute tolled until 18th birthday",
                "Fraudulent Concealment — statute tolled if defendant actively concealed malpractice"
            ],
            "filing_checklist": [
                {"item": "File Complaint", "deadline": "2028-05-10", "priority": "critical"},
                {"item": "Serve Defendant", "deadline": "2028-07-10", "priority": "high"},
                {"item": "Expert Witness Disclosure", "deadline": "2028-09-10", "priority": "high"},
                {"item": "Complete Discovery", "deadline": "2029-01-10", "priority": "medium"}
            ],
            "note": "MOCK DATA — Configure Groq API key for AI-generated SOL analysis."
        }
    
    prompt = f"""
    Generate a detailed Statute of Limitations analysis for this case.
    
    Case Details:
    - Case Type: {case_type}
    - Incident Date: {incident_date}
    - State: {state}
    
    Include:
    1. SOL deadline date
    2. Days remaining until deadline
    3. Applicable tolling exceptions (discovery rule, minority, fraudulent concealment, etc.)
    4. Filing checklist with critical dates (file complaint, serve defendant, expert disclosure, discovery)
    
    Return ONLY valid JSON with keys: case_type (string), incident_date (string), state (string), sol_deadline (string), days_remaining (number), tolling_exceptions (array of strings), filing_checklist (array of {{item, deadline, priority}}).
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a seasoned civil procedure expert specializing in statutes of limitations across all 50 states. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e), "tolling_exceptions": [], "filing_checklist": []}


def generate_trial_readiness(case_summary: str) -> dict:
    """
    Analyze case preparation and produce a 0-100 trial readiness score.
    """
    if not client:
        return {
            "readiness_score": 62,
            "overall_assessment": "Case shows moderate preparation. Strong liability theory but significant gaps in damages documentation and expert witness retention.",
            "gaps_identified": [
                "No retained expert witnesses identified",
                "Medical records incomplete — missing post-surgical follow-up notes",
                "Damages documentation insufficient — no lost wage verification",
                "Settlement demand not yet drafted",
                "Witness list incomplete"
            ],
            "recommendations": [
                "Retain medical expert within 30 days",
                "Request complete medical records from all treating facilities",
                "Obtain lost wage documentation from employer",
                "Draft initial settlement demand",
                "Complete witness interviews and finalize witness list"
            ],
            "category_scores": {
                "liability_theory": 78,
                "damages_evidence": 45,
                "expert_witnesses": 20,
                "discovery_completion": 65,
                "procedural_compliance": 85
            },
            "note": "MOCK DATA — Configure Groq API key for AI-generated analysis."
        }
    
    prompt = f"""
    Analyze the following case summary and produce a trial readiness score.
    
    Case Summary:
    {case_summary}
    
    Evaluate these categories (0-100 each):
    1. Liability theory strength
    2. Damages evidence quality
    3. Expert witness readiness
    4. Discovery completion
    5. Procedural compliance
    
    Include:
    - Overall readiness score (0-100)
    - Overall assessment paragraph
    - Gaps identified (list)
    - Recommendations (list)
    - Category scores
    
    Return ONLY valid JSON with keys: readiness_score (number), overall_assessment (string), gaps_identified (array of strings), recommendations (array of strings), category_scores (object).
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a veteran trial consultant who has prepared hundreds of cases for trial. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e), "gaps_identified": [], "recommendations": [], "category_scores": {}}


# =========================================================================
# Settlement Predictor — AI Endpoints
# =========================================================================

def predict_settlement(damages: float, case_type: str, state: str, liability_strength: str) -> dict:
    """
    Predict settlement range based on damages, case type, jurisdiction, and liability.
    """
    if not client:
        return {
            "predicted_range": {"low": 250000, "high": 450000},
            "best_estimate": 350000,
            "demand_framework": {
                "initial_demand": 525000,
                "minimum_acceptable": 280000,
                "anchor_strategy": "Demand at 150% of high estimate ($450K), anchor at $675K in mediation"
            },
            "litigation_strategy": "File in state court. Emphasize clear liability and documented damages. Consider early mediation after initial discovery.",
            "verdict_data": {
                "median_verdict": 375000,
                "plaintiff_win_rate": "62%",
                "verdict_range": "50K - 2.1M",
                "source": "Jury Verdict Research 2025"
            },
            "risk_factors": [
                "Comparative fault allegations expected",
                "Defendant has strong legal representation",
                "Jurisdiction is defense-friendly on similar cases"
            ],
            "note": "MOCK DATA — Configure Groq API key for AI-generated settlement analysis."
        }
    
    prompt = f"""
    Generate a detailed settlement prediction and analysis.
    
    Case Details:
    - Total Damages: ${damages:,.2f}
    - Case Type: {case_type}
    - State: {state}
    - Liability Strength: {liability_strength}
    
    Include:
    1. Predicted settlement range (low, high) and best estimate
    2. Demand framework (initial demand, minimum acceptable, anchor strategy)
    3. Litigation strategy
    4. Verdict data (median, plaintiff win rate, range, source)
    5. Risk factors (list)
    
    Return ONLY valid JSON with keys: predicted_range (object with low, high), best_estimate (number), demand_framework (object with initial_demand, minimum_acceptable, anchor_strategy), litigation_strategy (string), verdict_data (object with median_verdict, plaintiff_win_rate, verdict_range, source), risk_factors (array of strings).
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a senior settlement consultant with deep knowledge of verdict data, insurance adjuster behavior, and negotiation strategy across all 50 states. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e), "predicted_range": {"low": 0, "high": 0}, "best_estimate": 0}


# =========================================================================
# Medical Analysis — AI Endpoints
# =========================================================================

def analyze_medical_case(case_description: str) -> dict:
    """
    Analyze a medical case description for chronology, treatment gaps, and merit.
    """
    if not client:
        return {
            "medical_chronology": [
                {"date": "2026-04-15", "event": "Patient presented to ER with chest pain and shortness of breath", "source": "ER Triage Notes"},
                {"date": "2026-04-15", "event": "Diagnostic tests ordered: EKG, cardiac enzymes, chest X-ray", "source": "Physician Orders"},
                {"date": "2026-04-16", "event": "Elevated troponin levels detected — acute coronary syndrome diagnosed", "source": "Lab Results"},
                {"date": "2026-04-17", "event": "Cardiology consult — recommended urgent catheterization", "source": "Consult Note"},
                {"date": "2026-04-19", "event": "Cardiac catheterization performed — 90% LAD stenosis found and stented", "source": "Op Report"}
            ],
            "treatment_gaps": [
                {"gap": "4-hour delay in antibiotic administration", "severity": "HIGH", "details": "Antibiotics ordered at 19:15 but not administered until 23:15"},
                {"gap": "Missed troponin re-check at 6 hours", "severity": "MEDIUM", "details": "ACLS guidelines require troponin re-check at 6 hours; no re-check documented"}
            ],
            "merit_assessment": {
                "overall_merit": "Moderate-High",
                "score": 72,
                "strength_factors": ["Clear deviation from standard of care", "Documented timeline of delays"],
                "weakness_factors": ["Patient had pre-existing conditions", "Some records are incomplete"],
                "recommended_course": "Further investigation needed. Strong potential for medical malpractice claim with proper expert support."
            },
            "note": "MOCK DATA — Configure Groq API key for AI-generated analysis."
        }
    
    prompt = f"""
    Analyze this medical case description for a medical malpractice legal context.
    
    Case Description:
    {case_description}
    
    Generate:
    1. Medical chronology (events with dates, descriptions, and sources)
    2. Treatment gaps (any delays or gaps in care, with severity: HIGH/MEDIUM/LOW)
    3. Merit assessment (overall merit, score 0-100, strength factors, weakness factors, recommended course)
    
    Return ONLY valid JSON with keys: medical_chronology (array of {{date, event, source}}), treatment_gaps (array of {{gap, severity, details}}), merit_assessment (object with overall_merit, score, strength_factors (array), weakness_factors (array), recommended_course).
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a board-certified physician and medical-legal expert. Analyze cases for medical malpractice merit. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e), "medical_chronology": [], "treatment_gaps": [], "merit_assessment": {}}
