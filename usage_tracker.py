"""
LexiFlow Multi-Tier Usage-Based Metering System — DB-Backed.
Enforces document processing limits per tier and triggers billing alerts.
Integrates with ai_engine.py to block processing when limits are exceeded.

Tier Limits (per Business Plan):
- Standard:  50  docs/mo, $2.50/doc overage
- Professional: 250 docs/mo, $1.50/doc overage
- Enterprise: 500 docs/mo, custom pricing
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
    DOCUMENT_REVIEW = "document_review"


class UsageTier(str, Enum):
    FREE = "free"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class UsageTierConfig:
    tier: UsageTier
    monthly_document_limit: int
    overage_rate_per_doc: float
    ocr_page_rate: float
    monthly_chronology_limit: int
    overage_rate_per_chronology: float
    description: str


# Updated tier configs matching the LexiFlow Business Plan (3-Tier Revision)
TIER_CONFIGS = {
    UsageTier.STANDARD: UsageTierConfig(
        UsageTier.STANDARD, 50, 2.50, 0.15, 50, 2.50,
        "50 docs/mo included, $2.50/doc overage"
    ),
    UsageTier.PROFESSIONAL: UsageTierConfig(
        UsageTier.PROFESSIONAL, 250, 1.50, 0.10, 250, 1.50,
        "250 docs/mo included, $1.50/doc overage"
    ),
    UsageTier.ENTERPRISE: UsageTierConfig(
        UsageTier.ENTERPRISE, 500, 0.75, 0.05, 500, 0.75,
        "500 docs/mo included, $0.75/doc overage"
    ),
    UsageTier.FREE: UsageTierConfig(
        UsageTier.FREE, 0, 0.0, 0.0, 0, 0.0,
        "Demo tier — no document processing"
    ),
}


class UsageLimitExceeded(Exception):
    """Raised when a firm has exceeded their tier's document processing limit."""
    def __init__(self, firm_id, tier, current_count, limit, billing_period):
        self.firm_id = firm_id
        self.tier = tier
        self.current_count = current_count
        self.limit = limit
        self.billing_period = billing_period
        self.message = (
            f"Firm {firm_id} ({tier}) exceeded {limit} doc limit for {billing_period}. "
            f"Current: {current_count}. Processing blocked."
        )
        super().__init__(self.message)


class UsageTracker:
    """Tracks and enforces multi-tier usage limits. Persists to DB."""

    def __init__(self, db=None):
        self.db = db

    def get_tier_config(self, tier):
        try:
            return TIER_CONFIGS[UsageTier(tier)]
        except (ValueError, KeyError):
            return TIER_CONFIGS[UsageTier.STANDARD]

    def get_billing_period(self, d=None):
        return (d or datetime.utcnow()).strftime("%Y-%m")

    def _get_firm_tier(self, firm_id, db=None) -> str:
        """Get the current tier for a firm from DB."""
        s = db or self.db
        if not s:
            return "standard"
        try:
            fid = int(firm_id) if str(firm_id).isdigit() else 0
            firm = s.query(Firm).filter(Firm.id == fid).first()
            if firm and firm.plan_tier:
                return firm.plan_tier
        except Exception as e:
            logger.warning(f"Could not read firm tier: {e}")
        return "standard"

    # ===================== USAGE RECORDING =====================

    def record_usage(self, firm_id, doc_type, doc_name="", lead_id=None,
                     pages=0, time_ms=0, tokens=0, eligible=True, db=None):
        """Record a usage event (persisted to DB)."""
        s = db or self.db
        now = datetime.utcnow()
        period = self.get_billing_period(now)
        fid = int(firm_id) if str(firm_id).isdigit() else 0
        r = UsageRecord(
            firm_id=fid, lead_id=lead_id,
            document_type=doc_type,
            document_name=doc_name or f"{doc_type} - {now.isoformat()}",
            page_count=pages, processing_time_ms=time_ms,
            ai_tokens_used=tokens, overage_eligible=eligible,
            billing_period=period, recorded_at=now
        )
        if s:
            s.add(r)
            s.commit()
            s.refresh(r)
            rid = r.id
        else:
            rid = None
            logger.warning("No DB session for usage recording")
        return {
            "status": "recorded", "id": rid, "firm_id": firm_id,
            "document_type": doc_type, "billing_period": period
        }

    # ===================== LIMIT CHECKING & ENFORCEMENT =====================

    def get_current_count(self, firm_id, billing_period=None, db=None) -> int:
        """Get the number of documents processed by a firm in a billing period."""
        s = db or self.db
        if not s:
            return 0
        fid = int(firm_id) if str(firm_id).isdigit() else 0
        period = billing_period or self.get_billing_period()
        return s.query(UsageRecord).filter(
            UsageRecord.firm_id == fid,
            UsageRecord.billing_period == period
        ).count()

    def check_usage_limit(self, firm_id, tier=None, db=None) -> dict:
        """
        Pre-flight check: can this firm process more documents this billing period?
        Returns detailed status including whether limit is reached.
        """
        s = db or self.db
        if tier is None:
            tier = self._get_firm_tier(firm_id, s)
        period = self.get_billing_period()
        config = self.get_tier_config(tier)
        current = self.get_current_count(firm_id, period, s)
        remaining = max(0, config.monthly_document_limit - current)
        overage_docs = max(0, current - config.monthly_document_limit)
        overage_cost = round(overage_docs * config.overage_rate_per_doc, 2)

        return {
            "firm_id": firm_id,
            "tier": tier,
            "billing_period": period,
            "monthly_limit": config.monthly_document_limit,
            "current_usage": current,
            "remaining": remaining,
            "overage_documents": overage_docs,
            "estimated_overage_cost": overage_cost,
            "limit_reached": remaining <= 0,
            "can_process": remaining > 0,
        }

    def enforce_usage_limit(self, firm_id, tier=None, db=None):
        """
        Enforce the usage limit. Raises UsageLimitExceeded if limit is reached.
        Call this BEFORE processing a document to block over-limit usage.
        """
        s = db or self.db
        if tier is None:
            tier = self._get_firm_tier(firm_id, s)
        period = self.get_billing_period()
        config = self.get_tier_config(tier)
        current = self.get_current_count(firm_id, period, s)

        if current >= config.monthly_document_limit:
            raise UsageLimitExceeded(
                firm_id=firm_id, tier=tier,
                current_count=current, limit=config.monthly_document_limit,
                billing_period=period
            )
        return True

    def get_firm_history(self, firm_id, limit=50, offset=0, document_type=None, db=None) -> list:
        """Get detailed usage history for a firm."""
        s = db or self.db
        if not s:
            return []
        fid = int(firm_id) if str(firm_id).isdigit() else 0
        q = s.query(UsageRecord).filter(UsageRecord.firm_id == fid)
        if document_type:
            q = q.filter(UsageRecord.document_type == document_type)
        q = q.order_by(UsageRecord.recorded_at.desc()).offset(offset).limit(limit)
        records = q.all()
        return [
            {
                "id": r.id, "document_type": r.document_type,
                "document_name": r.document_name,
                "page_count": r.page_count, "processing_time_ms": r.processing_time_ms,
                "ai_tokens_used": r.ai_tokens_used,
                "overage_eligible": r.overage_eligible,
                "billing_period": r.billing_period,
                "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None,
            }
            for r in records
        ]

    # ===================== TIER MANAGEMENT =====================

    def set_firm_tier(self, firm_id, tier, db=None):
        """Set the billing tier for a firm (persisted to Firm model)."""
        s = db or self.db
        if not s:
            logger.error("No DB session for set_firm_tier")
            return
        fid = int(firm_id) if str(firm_id).isdigit() else 0
        firm = s.query(Firm).filter(Firm.id == fid).first()
        if firm:
            firm.plan_tier = tier
            s.commit()
        else:
            raise ValueError(f"Firm {firm_id} not found")

    # ===================== USAGE SUMMARY =====================

    def calculate_summary(self, firm_id, period=None, tier="standard", db=None):
        """Calculate usage summary with overage costs."""
        s = db or self.db
        p = period or self.get_billing_period()
        tc = self.get_tier_config(tier)
        fid = int(firm_id) if str(firm_id).isdigit() else 0
        docs = chrons = ocr_pages = time_total = tokens = 0

        if s:
            recs = s.query(UsageRecord).filter(
                UsageRecord.firm_id == fid,
                UsageRecord.billing_period == p
            ).all()
            docs = len(recs)
            for r in recs:
                if r.document_type == DocumentType.MEDICAL_CHRONOLOGY:
                    chrons += 1
                if r.document_type == DocumentType.OCR_PROCESSING:
                    ocr_pages += r.page_count or 0
                time_total += r.processing_time_ms or 0
                tokens += r.ai_tokens_used or 0

        ov = max(0, docs - tc.monthly_document_limit)
        ov_ch = max(0, chrons - tc.monthly_chronology_limit)
        eff = max(ov, ov_ch)
        cost = eff * tc.overage_rate_per_doc + ocr_pages * tc.ocr_page_rate

        return type('UsageSummary', (), {
            'firm_id': firm_id, 'billing_period': p, 'tier': tier,
            'total_documents': docs, 'total_chronologies': chrons,
            'total_ocr_pages': ocr_pages,
            'included_documents': tc.monthly_document_limit,
            'overage_documents': eff,
            'estimated_overage_cost': round(cost, 2),
            'total_processing_time_ms': time_total,
            'total_ai_tokens': tokens,
            'flat_rate': 69.0,
            'total_estimated_bill': round(69.0 + cost, 2),
        })()


# Singleton instance for import-based access
usage_tracker = UsageTracker()