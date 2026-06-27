from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import datetime
import json
import logging
from integration_engine import integration_engine

logger = logging.getLogger(__name__)

def get_weekly_stats(db: Session, firm_id: int):
    seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    
    # 1. Total Leads
    total_leads = db.query(models.Lead).filter(
        models.Lead.firm_id == firm_id,
        models.Lead.created_at >= seven_days_ago
    ).count()
    
    # 2. Qualified Leads (Score >= 70 or status in ['qualified', 'retainer_sent', 'signed'])
    qualified_leads = db.query(models.Lead).filter(
        models.Lead.firm_id == firm_id,
        models.Lead.created_at >= seven_days_ago,
        (models.Lead.qualification_score >= 70) | (models.Lead.status.in_(['qualified', 'retainer_sent', 'signed']))
    ).count()
    
    # 3. Conversion Rate
    conversion_rate = (qualified_leads / total_leads * 100) if total_leads > 0 else 0
    
    # 4. Top Leads
    top_leads_raw = db.query(models.Lead).filter(
        models.Lead.firm_id == firm_id,
        models.Lead.created_at >= seven_days_ago
    ).order_by(models.Lead.qualification_score.desc()).limit(5).all()
    
    top_leads = []
    for l in top_leads_raw:
        top_leads.append({
            "id": l.id,
            "full_name": l.full_name or "Anonymous",
            "case_type": l.case_type,
            "score": l.qualification_score,
            "summary": l.ai_summary,
            "created_at": l.created_at.isoformat()
        })
    
    # 5. Documents Analyzed
    docs_analyzed = db.query(models.Document).join(models.Lead).filter(
        models.Lead.firm_id == firm_id,
        models.Document.uploaded_at >= seven_days_ago
    ).count()
    
    return {
        "total_leads": total_leads,
        "qualified_leads": qualified_leads,
        "conversion_rate": round(conversion_rate, 1),
        "top_leads": top_leads,
        "docs_analyzed": docs_analyzed,
        "period": "Last 7 Days"
    }

async def generate_and_send_report(db: Session, firm: models.Firm):
    stats = get_weekly_stats(db, firm.id)
    
    # Format the report
    subject = f"Weekly Lead Report: {firm.name}"
    
    top_leads_text = ""
    for lead in stats['top_leads']:
        score = lead['score'] if lead['score'] else 0
        top_leads_text += f"- {lead['full_name']} ({lead['case_type'] or 'General'}): Score {score}/100\n"
        if lead['summary']:
            summary_snippet = lead['summary'][:150].replace('\n', ' ')
            top_leads_text += f"  Summary: {summary_snippet}...\n"
            
    body = f"""
Dear {firm.name} Team,

Here is your weekly LexiFlow Technologies Inc lead summary for the period of {stats['period']}.

--- PERFORMANCE METRICS ---
Total New Leads: {stats['total_leads']}
Qualified Leads: {stats['qualified_leads']}
Conversion Rate: {stats['conversion_rate']}%
Documents Analyzed: {stats['docs_analyzed']}

--- TOP QUALIFIED LEADS ---
{top_leads_text if top_leads_text else "No leads captured this week."}

---
Manage your leads at: https://app.lexiflow.co/dashboard

Best regards,
LexiFlow Technologies Inc Agent
    """
    
    # Get recipient email from firm config or default to info@lexiflow.co
    recipient_email = None
    if firm.api_config_json:
        try:
            config = json.loads(firm.api_config_json)
            recipient_email = config.get("report_recipient_email") or config.get("postmark_recipient_email")
        except:
            pass
            
    if not recipient_email:
        # Try to find a user email for this firm
        user = db.query(models.User).filter(models.User.firm_id == firm.id).first()
        if user:
            recipient_email = user.email
            
    if not recipient_email:
        recipient_email = "info@lexiflow.co" # Fallback
        
    result = await integration_engine.send_postmark_email(
        to_email=recipient_email,
        subject=subject,
        body=body,
        firm=firm
    )
    
    return {
        "status": "success" if result.get("status") != "error" else "error",
        "recipient": recipient_email,
        "stats": {
            "total_leads": stats["total_leads"],
            "qualified_leads": stats["qualified_leads"],
            "conversion_rate": stats["conversion_rate"],
            "docs_analyzed": stats["docs_analyzed"]
        }
    }
