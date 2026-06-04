"""
LexiFlow Usage-Based Fee Tracking Engine — DB-Backed Version
Persists all records to database. Survives restarts.
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from models import UsageRecord, Firm

logger = logging.getLogger(__name__)

class DocumentType(str, Enum):
    MEDICAL_CHRONOLOGY = "medical_chronology"
    OCR_PROCESSING = "ocr_processing"
    LEAD_QUALIFICATION = "lead_qualification"

class UsageTier(str, Enum):
    FREE = "free"; STANDARD = "standard"; PROFESSIONAL = "professional"; ENTERPRISE = "enterprise"

@dataclass
class UsageTierConfig:
    tier: UsageTier; monthly_document_limit: int; overage_rate_per_doc: float
    ocr_page_rate: float; monthly_chronology_limit: int; overage_rate_per_chronology: float; description: str

TIER_CONFIGS = {
    UsageTier.STANDARD: UsageTierConfig(UsageTier.STANDARD, 50, 2.50, 0.15, 50, 2.50, "50 docs/mo, $2.50 overage"),
    UsageTier.PROFESSIONAL: UsageTierConfig(UsageTier.PROFESSIONAL, 200, 1.50, 0.10, 200, 1.50, "200 docs/mo, $1.50 overage"),
    UsageTier.ENTERPRISE: UsageTierConfig(UsageTier.ENTERPRISE, 99999, 0.50, 0.05, 99999, 0.50, "Custom limits"),
    UsageTier.FREE: UsageTierConfig(UsageTier.FREE, 0, 0.0, 0.0, 0, 0.0, "Flat-rate only"),
}

class UsageTracker:
    """Tracks usage — persists to DB. No in-memory storage."""
    def __init__(self, db=None): self.db = db
    def get_tier_config(self, tier):
        try: return TIER_CONFIGS[UsageTier(tier)]
        except: return TIER_CONFIGS[UsageTier.STANDARD]
    def get_billing_period(self, d=None): return (d or datetime.utcnow()).strftime("%Y-%m")
    def record_usage(self, firm_id, doc_type, doc_name="", lead_id=None, pages=0, time_ms=0, tokens=0, eligible=True, db=None):
        s = db or self.db; now = datetime.utcnow(); period = self.get_billing_period(now)
        r = UsageRecord(firm_id=int(firm_id) if str(firm_id).isdigit() else 0, lead_id=lead_id,
            document_type=doc_type, document_name=doc_name or f"{doc_type} - {now.isoformat()}",
            page_count=pages, processing_time_ms=time_ms, ai_tokens_used=tokens,
            overage_eligible=eligible, billing_period=period, recorded_at=now)
        if s: s.add(r); s.commit(); s.refresh(r); rid = r.id
        else: rid = None; logger.warning("No DB session")
        return {"status":"recorded","id":rid,"firm_id":firm_id,"document_type":doc_type,"billing_period":period}
    def calculate_summary(self, firm_id, period=None, tier="standard", db=None):
        s = db or self.db; p = period or self.get_billing_period(); tc = self.get_tier_config(tier)
        fid = int(firm_id) if str(firm_id).isdigit() else 0
        docs=chrons=ocr_pages=time_total=tokens=0
        if s:
            recs = s.query(UsageRecord).filter(UsageRecord.firm_id==fid, UsageRecord.billing_period==p).all()
            docs = len(recs)
            for r in recs:
                if r.document_type==DocumentType.MEDICAL_CHRONOLOGY: chrons+=1
                if r.document_type==DocumentType.OCR_PROCESSING: ocr_pages+=r.page_count or 0
                time_total+=r.processing_time_ms or 0; tokens+=r.ai_tokens_used or 0
        ov = max(0, docs-tc.monthly_document_limit)
        ov_ch = max(0, chrons-tc.monthly_chronology_limit)
        eff = max(ov, ov_ch); cost = eff*tc.overage_rate_per_doc + ocr_pages*tc.ocr_page_rate
        return type('UsageSummary',(),{'firm_id':firm_id,'billing_period':p,'tier':tier,
            'total_documents':docs,'total_chronologies':chrons,'total_ocr_pages':ocr_pages,
            'included_documents':tc.monthly_document_limit,'overage_documents':eff,
            'estimated_overage_cost':round(cost,2),'total_processing_time_ms':time_total,
            'total_ai_tokens':tokens,'flat_rate':69.0,'total_estimated_bill':round(69.0+cost,2)})()

usage_tracker = UsageTracker()