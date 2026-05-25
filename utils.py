from sqlalchemy.orm import Session
from . import models
import datetime

def log_usage(db: Session, firm_id: int, usage_type: str, quantity: float = 1.0, details: str = None):
    """
    Log usage for a firm.
    usage_type: document_analysis, voice_minutes, email_intake
    """
    if firm_id is None:
        return
        
    usage = models.Usage(
        firm_id=firm_id,
        usage_type=usage_type,
        quantity=quantity,
        details=details,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(usage)
    db.commit()
