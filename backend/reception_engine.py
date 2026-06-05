import json
import logging
from sqlalchemy.orm import Session
import models, ai_engine, integration_engine, utils

logger = logging.getLogger(__name__)

VOICE_MAPPING = {
    "sarah": "9585607e-7259-430b-9363-2287f394c861",
    "james": "69267136-1bdc-40d0-81f1-b92209705a39",
    "elena": "54497c6d-5573-4560-84a7-b24888005b63"
}

async def handle_vapi_message(payload: dict, db: Session):
    """
    Handle incoming messages from Vapi Server URL.
    Reference: https://docs.vapi.ai/server-url
    """
    message_type = payload.get("message", {}).get("type")
    
    if message_type == "assistant-request":
        # Extract firm_slug from metadata
        # Vapi metadata can be at the root of 'message' or nested in 'call'
        assistant_metadata = payload.get("message", {}).get("metadata") or \
                             payload.get("message", {}).get("call", {}).get("metadata", {})
        
        firm_slug = assistant_metadata.get("firm_slug")
        
        firm = None
        if firm_slug:
            firm = db.query(models.Firm).filter(models.Firm.slug == firm_slug).first()
            
        if not firm or not firm.voice_enabled:
            # Gracefully handle disabled voice or unknown firm
            return {
                "assistant": {
                    "name": "Service Unavailable",
                    "firstMessage": "I'm sorry, but this service is currently unavailable. Please try again later.",
                    "model": {
                        "provider": "openai",
                        "model": "gpt-4o",
                        "systemPrompt": "Inform the user that the service is unavailable and they should call back later or visit the website."
                    }
                }
            }

        voice_config = json.loads(firm.voice_config_json) if firm.voice_config_json else {}
        voice_slug = voice_config.get("voice_id", "sarah")
        voice_id = VOICE_MAPPING.get(voice_slug, VOICE_MAPPING["sarah"])
        first_message = voice_config.get("greeting", f"Hello, thank you for calling {firm.name}. This is Lexi, how can I help you today?")
        
        return {
            "assistant": {
                "name": f"{firm.name} AI Assistant",
                "firstMessage": first_message,
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "systemPrompt": f"You are Lexi, a professional legal intake assistant for {firm.name}. Your goal is to gather the caller's name, case details, and contact info with empathy. Do not give legal advice. Keep responses concise for voice interaction."
                },
                "voice": {
                    "provider": "cartesia",
                    "voiceId": voice_id
                }
            }
        }
    
    elif message_type == "tool-call":
        # Handle tool calls from the voice AI (e.g., check availability, create lead early)
        return {"results": [{"toolCallId": payload["message"]["toolCalls"][0]["id"], "result": "Success"}]}

    elif message_type == "end-of-call-report":
        # Call ended, save the lead and transcript
        call_data = payload.get("message", {}).get("call", {})
        transcript = payload.get("message", {}).get("transcript", "")
        summary = payload.get("message", {}).get("summary", "")
        
        # Extract metadata if available (e.g., firm_id passed in assistant metadata)
        firm_id = None
        assistant_metadata = payload.get("message", {}).get("assistant", {}).get("metadata", {})
        firm_slug = assistant_metadata.get("firm_slug")
        
        if firm_slug:
            firm = db.query(models.Firm).filter(models.Firm.slug == firm_slug).first()
            if firm:
                firm_id = firm.id

        # Create the lead
        lead = models.Lead(
            firm_id=firm_id,
            source="Voice AI",
            description=f"Voice Call Transcript:\n{transcript}",
            ai_summary=summary,
            phone=call_data.get("customer", {}).get("number")
        )
        db.add(lead)
        db.flush()
        
        # Log voice usage
        duration_seconds = call_data.get("duration", 0)
        minutes = duration_seconds / 60.0
        if firm_id:
            utils.log_usage(db, firm_id, "voice_minutes", quantity=round(minutes, 2), details=f"Call ID: {call_data.get('id')}")

        # Save transcript as messages
        # Vapi transcript is usually a single string or list of objects
        # For simplicity in prototype, we save the whole thing as one or split it
        # Here we'll just save the summary as a system note and transcript in description
        
        # Attempt to qualify lead based on transcript
        if transcript:
            score, status, ai_summary, client_info, case_value = ai_engine.qualify_lead(transcript)
            lead.qualification_score = score
            lead.status = status
            lead.ai_summary = ai_summary
            lead.case_value_estimate = case_value
            if client_info:
                lead.full_name = client_info.get("full_name")
                lead.email = client_info.get("email")
                if client_info.get("phone"):
                    lead.phone = client_info.get("phone")

        db.commit()
        return {"status": "success", "lead_id": lead.id}

    return {"status": "received"}

async def handle_postmark_inbound(payload: dict, db: Session):
    """
    Handle incoming JSON from Postmark Inbound Webhook.
    Reference: https://postmarkapp.com/developer/user-guide/inbound-webhook
    """
    from_email = payload.get("From")
    from_name = payload.get("FromName")
    subject = payload.get("Subject")
    text_body = payload.get("TextBody")
    
    # Identify firm by the "To" address or a specific header/tag if needed
    # For now, we'll look for a firm slug in the 'To' address if it's in format firm+slug@lexiflow.co
    firm_id = None
    to_emails = payload.get("ToFull", [])
    for to in to_emails:
        email_addr = to.get("Email", "")
        if "+" in email_addr:
            slug = email_addr.split("+")[1].split("@")[0]
            firm = db.query(models.Firm).filter(models.Firm.slug == slug).first()
            if firm:
                firm_id = firm.id
                break

    lead = models.Lead(
        firm_id=firm_id,
        full_name=from_name,
        email=from_email,
        source="Email",
        description=f"Subject: {subject}\n\n{text_body}"
    )
    db.add(lead)
    db.flush()
    
    # Log email usage
    if firm_id:
        utils.log_usage(db, firm_id, "email_intake", quantity=1.0, details=f"From: {from_email}")

    # Qualify lead
    if text_body:
        score, status, ai_summary, client_info, case_value = ai_engine.qualify_lead(text_body)
        lead.qualification_score = score
        lead.status = status
        lead.ai_summary = ai_summary
        lead.case_value_estimate = case_value

    db.commit()

    # --- Auto-Reply Logic ---
    if firm_id:
        firm = db.query(models.Firm).filter(models.Firm.id == firm_id).first()
        if firm and firm.email_enabled:
            try:
                email_config = json.loads(firm.email_config_json) if firm.email_config_json else {}
                template = email_config.get("template")
                
                if template:
                    # Comprehensive variable replacement
                    first_name = from_name.split()[0] if from_name else "there"
                    intake_url = f"https://lexiflow.co/demo.html?lead_id={lead.id}" # Base URL could be config-driven later
                    tracking_id = str(lead.id)
                    
                    reply_body = template
                    reply_body = reply_body.replace("{{full_name}}", from_name or "there")
                    reply_body = reply_body.replace("{{first_name}}", first_name)
                    reply_body = reply_body.replace("{{firm_name}}", firm.name)
                    reply_body = reply_body.replace("{{case_type}}", lead.case_type or "your inquiry")
                    reply_body = reply_body.replace("{{intake_url}}", intake_url)
                    reply_body = reply_body.replace("{{tracking_id}}", tracking_id)
                    
                    # Send via integration engine
                    await integration_engine.integration_engine.send_postmark_email(
                        to_email=from_email,
                        subject=f"Re: {subject}" if subject else f"Thank you for contacting {firm.name}",
                        body=reply_body,
                        firm=firm
                    )
                    logger.info(f"Auto-reply sent to {from_email} for firm {firm.name}")
            except Exception as e:
                logger.error(f"Failed to send auto-reply: {str(e)}")

    return {"status": "success", "lead_id": lead.id}
