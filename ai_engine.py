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

def analyze_document_image(file_path, filename):
    """
    Use AI Vision to extract key legal data from a document image.
    """
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
                {"role": "system", "content": "You are Lexi, the LexiFlow AI Assistant. You are professional, empathetic, and expert in legal intake. Your goal is to help potential clients understand how LexiFlow can help their firm, answer general questions about the platform, or begin a case intake.\n\nKey LexiFlow Facts:\n- 391% conversion boost for law firms.\n- Recaptures $12,000+ in billable hours per month.\n- 24/7 availability for lead capture and qualification.\n- Uses Reasoning AI (LLMs) instead of legacy Decision Trees to understand case nuances.\n- Direct sync to Clio, MyCase, and Filevine.\n- LexiFlow is NOT a law firm and does NOT provide legal advice.\n- You are multilingual and can converse fluently in Spanish, French, and other languages if the user initiates.\n\nIf a user wants to start an intake, guide them through it. If they want a demo, suggest clicking the 'Request Demo' button." + kb_info},
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

def analyze_document_text(text, filename):
    """
    Use AI to extract key legal data from document text.
    """
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

def generate_medical_chronology(transcript):
    """
    Generate a structured medical chronology from a legal intake transcript.
    """
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
    Main entry point for DepoLens AI analysis.
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

    # Real AI logic (Simplified version of DepoLens logic)
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
