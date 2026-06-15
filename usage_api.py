"""
FastAPI router for Usage-Based Fee tracking and billing endpoints.
All usage records persisted to database via SQLAlchemy (UsageRecord model).
No in-memory storage. Survives restarts.

Endpoints:
- POST /api/usage/record — Record a usage event (persisted to DB)
- GET /api/usage/summary/{firm_id} — Usage summary with overage costs (DB query)
- GET /api/usage/history/{firm_id} — Detailed usage history (DB query)
- GET /api/usage/check-limit/{firm_id} — Pre-flight limit check (DB count)
- PUT /api/usage/tier/{firm_id} — Set firm billing tier (persisted to Firm model)
- GET /api/usage/tiers — List available tiers and pricing
- GET /api/usage/stats — Global usage statistics (DB queries)
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import UsageRecord, Firm
from usage_tracker import UsageTracker, UsageTier, TIER_CONFIGS, DocumentType, usage_tracker

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/usage", tags=["Usage & Billing"])


@router.post("/record")
async def record_usage(
    firm_id: str = Body(...), document_type: str = Body(...),
    document_name: str = Body(""), lead_id: Optional[int] = Body(None),
    page_count: int = Body(0), processing_time_ms: int = Body(0),
    ai_tokens_used: int = Body(0), overage_eligible: bool = Body(True),
    db: Session = Depends(get_db),
):
    if document_type not in [dt.value for dt in DocumentType]:
        raise HTTPException(400, f"Invalid document_type")
    return usage_tracker.record_usage(firm_id=firm_id, document_type=document_type,
        document_name=document_name, lead_id=lead_id, page_count=page_count,
        processing_time_ms=processing_time_ms, ai_tokens_used=ai_tokens_used,
        overage_eligible=overage_eligible, db=db)


@router.get("/summary/{firm_id}")
async def get_usage_summary(firm_id: str = Path(...),
    billing_period: Optional[str] = Query(None), tier: str = Query("standard"),
    db: Session = Depends(get_db)):
    s = usage_tracker.calculate_summary(firm_id=firm_id, billing_period=billing_period, tier=tier, db=db)
    return {"firm_id": s.firm_id, "billing_period": s.billing_period, "tier": s.tier,
        "flat_rate": s.flat_rate, "total_documents": s.total_documents,
        "total_chronologies": s.total_chronologies, "total_ocr_pages": s.total_ocr_pages,
        "included_documents": s.included_documents, "overage_documents": s.overage_documents,
        "estimated_overage_cost": s.estimated_overage_cost, "total_estimated_bill": s.total_estimated_bill}


@router.get("/history/{firm_id}")
async def get_usage_history(firm_id: str = Path(...), limit: int = Query(50, le=500),
    offset: int = Query(0), document_type: Optional[str] = Query(None), db: Session = Depends(get_db)):
    records = usage_tracker.get_firm_history(firm_id=firm_id, limit=limit, offset=offset,
        document_type=document_type, db=db)
    return {"firm_id": firm_id, "total": len(records), "offset": offset, "limit": limit, "records": records}


@router.get("/check-limit/{firm_id}")
async def check_usage_limit(firm_id: str = Path(...), tier: str = Query("standard"),
    db: Session = Depends(get_db)):
    return usage_tracker.check_usage_limit(firm_id=firm_id, tier=tier, db=db)


@router.put("/tier/{firm_id}")
async def set_firm_tier(firm_id: str = Path(...), tier: str = Body(..., embed=True),
    db: Session = Depends(get_db)):
    if tier not in [t.value for t in UsageTier]:
        raise HTTPException(400, f"Invalid tier")
    usage_tracker.set_firm_tier(firm_id=firm_id, tier=tier, db=db)
    config = usage_tracker.get_tier_config(tier)
    return {"status": "updated", "firm_id": firm_id, "tier": tier,
        "monthly_limit": config.monthly_document_limit, "overage_rate": config.overage_rate_per_doc,
        "ocr_page_rate": config.ocr_page_rate}


@router.get("/tiers")
async def list_tiers():
    return {"tiers": [{"name": t.value, "description": c.description,
        "monthly_document_limit": c.monthly_document_limit,
        "overage_rate_per_doc": c.overage_rate_per_doc, "ocr_page_rate": c.ocr_page_rate}
        for t, c in TIER_CONFIGS.items()], "flat_rate_monthly": 69.0}


@router.get("/stats")
async def get_global_stats(db: Session = Depends(get_db)):
    firms_with_usage = db.query(UsageRecord.firm_id).distinct().count()
    total_docs = db.query(UsageRecord).count()
    total_chronologies = db.query(UsageRecord).filter(UsageRecord.document_type == DocumentType.MEDICAL_CHRONOLOGY).count()
    ocr_records = db.query(UsageRecord).filter(UsageRecord.document_type == DocumentType.OCR_PROCESSING).all()
    total_ocr_pages = sum(r.page_count or 0 for r in ocr_records)
    total_tokens = db.query(db.func.coalesce(db.func.sum(UsageRecord.ai_tokens_used), 0)).scalar()
    estimated_revenue = firms_with_usage * 69.0
    for r in ocr_records: estimated_revenue += (r.page_count or 0) * 0.15
    overage_count = max(0, total_docs - (firms_with_usage * 50))
    estimated_revenue += overage_count * 1.50
    return {"total_firms": firms_with_usage, "total_documents_processed": total_docs,
        "total_chronologies": total_chronologies, "total_ocr_pages": total_ocr_pages,
        "total_ai_tokens_consumed": total_tokens or 0,
        "estimated_monthly_revenue": round(estimated_revenue, 2)}