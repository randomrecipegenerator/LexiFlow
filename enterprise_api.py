"""
LexiFlow Enterprise Modules Mock API.

Provides mock data endpoints for the 4 Enterprise modules:
1. Discovery-Vault™ — AI-powered discovery document analysis
2. Settlement-Predictor Pro™ — AI case valuation & settlement prediction
3. DepoLens™ — Deposition intelligence & transcript analysis
4. Compliance-Shield™ — HIPAA/regulatory compliance monitoring

These endpoints are used by the Enterprise landing pages and Dashboard
to showcase module capabilities with realistic demo data.
"""
import json
import logging
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from . import damage_caps as damage_caps_utils

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/enterprise", tags=["Enterprise Modules"])


# =========================================================================
# Mock Data Generators
# =========================================================================

def _random_id() -> str:
    return ''.join(random.choices('abcdef0123456789', k=24))


def _random_date(days_ago: int = 365) -> str:
    return (datetime.utcnow() - timedelta(days=random.randint(1, days_ago))).strftime("%Y-%m-%d")


# =========================================================================
# 1. Discovery-Vault™ — AI Discovery Document Analysis
# =========================================================================

MOCK_DISCOVERY_CASES = [
    {
        "id": "dv-001",
        "case_name": "Martinez v. St. Mary's Medical Center",
        "case_type": "Medical Malpractice",
        "total_documents": 1247,
        "analyzed_documents": 1247,
        "processing_status": "complete",
        "key_findings": [
            "17 nursing notes contradict shift change testimony",
            "Surgical count discrepancy: sponge count off by 1",
            "Consent form signed 2 hours AFTER procedure started",
            "3 emails show internal concern about staffing ratios"
        ],
        "critical_docs": 23,
        "review_hours_saved": 186,
        "last_updated": "2026-06-04T14:30:00Z",
    },
    {
        "id": "dv-002",
        "case_name": "Johnson v. PharmaCare Inc.",
        "case_type": "Product Liability",
        "total_documents": 3421,
        "analyzed_documents": 2890,
        "processing_status": "processing",
        "key_findings": [
            "Internal memo acknowledges adverse event reporting lag",
            "15 similar complaints flagged across 3 states",
            "Marketing materials contradict FDA-approved labeling"
        ],
        "critical_docs": 41,
        "review_hours_saved": 412,
        "last_updated": "2026-06-05T09:15:00Z",
    },
    {
        "id": "dv-003",
        "case_name": "Estate of Williams v. Northside Nursing Home",
        "case_type": "Nursing Home Neglect",
        "total_documents": 856,
        "analyzed_documents": 856,
        "processing_status": "complete",
        "key_findings": [
            "Weight loss chart shows 18lb decrease over 6 weeks — undocumented",
            "Pressure injury photos show Stage II → Stage IV progression",
            "Staffing logs show below-minimum ratios on 42 of 60 days"
        ],
        "critical_docs": 17,
        "review_hours_saved": 128,
        "last_updated": "2026-06-03T16:45:00Z",
    },
]


@router.get("/discovery/overview")
async def get_discovery_overview():
    """Get overview of all Discovery-Vault™ cases."""
    return {
        "total_cases": len(MOCK_DISCOVERY_CASES),
        "total_documents_processed": sum(c["analyzed_documents"] for c in MOCK_DISCOVERY_CASES),
        "total_hours_saved": sum(c["review_hours_saved"] for c in MOCK_DISCOVERY_CASES),
        "critical_docs_found": sum(c["critical_docs"] for c in MOCK_DISCOVERY_CASES),
        "cases": MOCK_DISCOVERY_CASES,
    }


@router.get("/discovery/case/{case_id}")
async def get_discovery_case(case_id: str):
    """Get detailed discovery analysis for a specific case."""
    for case in MOCK_DISCOVERY_CASES:
        if case["id"] == case_id:
            return {
                **case,
                "document_breakdown": {
                    "medical_records": random.randint(300, 800),
                    "deposition_transcripts": random.randint(10, 50),
                    "correspondence": random.randint(50, 200),
                    "billing_records": random.randint(20, 100),
                    "expert_reports": random.randint(5, 20),
                },
                "ai_analysis_summary": (
                    f"AI analysis of {case['total_documents']} documents complete. "
                    f"Identified {case['critical_docs']} critical documents requiring immediate attention. "
                    f"Estimated {case['review_hours_saved']} attorney hours saved."
                ),
            }
    raise HTTPException(404, detail=f"Discovery case {case_id} not found")


# =========================================================================
# 2. Settlement-Predictor Pro™ — AI Case Valuation
# =========================================================================

MOCK_SETTLEMENT_CASES = [
    {
        "id": "sp-001",
        "case_name": "Rodriguez v. County General Hospital",
        "case_type": "Medical Malpractice – Surgical Error",
        "jurisdiction": "California, Los Angeles County",
        "demand_amount": 3500000.00,
        "predicted_range": {"low": 1250000, "high": 2200000},
        "ai_confidence": 87.4,
        "comparable_settlements": 142,
        "key_factors": [
            {"factor": "Clear liability (sponge left in abdomen)", "impact": "positive", "weight": "high"},
            {"factor": "Plaintiff age (42, working professional)", "impact": "positive", "weight": "medium"},
            {"factor": "Prior medical history includes similar surgery", "impact": "negative", "weight": "medium"},
        ],
        "recommended_strategy": "Mediate at $1.8M; strong liability case supports above-median recovery",
        "estimated_trial_value": 3100000.00,
        "probability_of_plaintiff_verdict": 72.3,
    },
    {
        "id": "sp-002",
        "case_name": "Thompson v. City Transit Authority",
        "case_type": "Personal Injury – Auto Accident",
        "jurisdiction": "New York, Kings County",
        "demand_amount": 850000.00,
        "predicted_range": {"low": 320000, "high": 580000},
        "ai_confidence": 91.2,
        "comparable_settlements": 287,
        "key_factors": [
            {"factor": "Soft tissue injury only (no fractures)", "impact": "negative", "weight": "medium"},
            {"factor": "Defendant admitted fault at scene", "impact": "positive", "weight": "high"},
            {"factor": "12 weeks of PT documented", "impact": "positive", "weight": "medium"},
        ],
        "recommended_strategy": "Demand $650K; strong liability but damages limited by injury type",
        "estimated_trial_value": 750000.00,
        "probability_of_plaintiff_verdict": 85.1,
    },
]


@router.get("/settlement/overview")
async def get_settlement_overview():
    """Get overview of all Settlement-Predictor Pro™ cases."""
    return {
        "total_cases_analyzed": len(MOCK_SETTLEMENT_CASES),
        "average_confidence": round(sum(c["ai_confidence"] for c in MOCK_SETTLEMENT_CASES) / len(MOCK_SETTLEMENT_CASES), 1),
        "total_demand_amount": sum(c["demand_amount"] for c in MOCK_SETTLEMENT_CASES),
        "total_predicted_low": sum(c["predicted_range"]["low"] for c in MOCK_SETTLEMENT_CASES),
        "total_predicted_high": sum(c["predicted_range"]["high"] for c in MOCK_SETTLEMENT_CASES),
        "comparable_settlements_in_db": sum(c["comparable_settlements"] for c in MOCK_SETTLEMENT_CASES),
        "cases": [
            {
                "id": c["id"],
                "case_name": c["case_name"],
                "case_type": c["case_type"],
                "demand_amount": c["demand_amount"],
                "predicted_range": c["predicted_range"],
                "ai_confidence": c["ai_confidence"],
            }
            for c in MOCK_SETTLEMENT_CASES
        ],
    }


@router.get("/settlement/case/{case_id}")
async def get_settlement_case(case_id: str):
    """Get detailed settlement prediction for a specific case, including damage cap analysis."""
    for case in MOCK_SETTLEMENT_CASES:
        if case["id"] == case_id:
            # Extract state code from jurisdiction (e.g. "California, Los Angeles County" -> "CA")
            state_code = _extract_state_code(case["jurisdiction"])
            damage_cap_analysis = None
            if state_code:
                cap_data = damage_caps_utils.get_damage_cap(state_code)
                if cap_data:
                    # Calculate what the estimated trial value would be capped at
                    ne_portion = min(case["estimated_trial_value"] * 0.6, case["demand_amount"] * 0.5)
                    econ_portion = case["estimated_trial_value"] - ne_portion
                    capped = damage_caps_utils.calculate_capped_value(state_code, ne_portion, econ_portion)
                    damage_cap_analysis = {
                        "state_code": state_code,
                        "state_name": cap_data.state,
                        "non_economic_cap": cap_data.non_economic_cap,
                        "total_cap": cap_data.total_cap,
                        "max_payout_without_caps": round(case["estimated_trial_value"], 2),
                        "max_payout_with_caps": round(max(capped["capped_total"], capped["capped_total"]), 2),
                        "reduction_due_to_caps": round(capped["reduction_amount"], 2),
                        "cap_applies": capped["cap_applied"],
                        "cap_details": capped["cap_details"],
                        "citation": cap_data.citation,
                    }
            return {
                **case,
                "damage_cap_analysis": damage_cap_analysis,
            }
    raise HTTPException(404, detail=f"Settlement case {case_id} not found")


def _extract_state_code(jurisdiction: str) -> str:
    """Extract state code from a jurisdiction string like 'California, Los Angeles County'."""
    if not jurisdiction:
        return None
    # Look up the state name in our caps data
    jurisdiction_lower = jurisdiction.lower()
    for code, cap in damage_caps_utils.STATE_DAMAGE_CAPS.items():
        if cap.state.lower() in jurisdiction_lower:
            return code
    # Fallback: try common state name mapping
    state_map = {
        "california": "CA", "new york": "NY", "texas": "TX", "florida": "FL",
        "illinois": "IL", "pennsylvania": "PA", "ohio": "OH", "georgia": "GA",
        "michigan": "MI", "new jersey": "NJ", "virginia": "VA", "washington": "WA",
        "arizona": "AZ", "massachusetts": "MA", "tennessee": "TN", "indiana": "IN",
        "missouri": "MO", "maryland": "MD", "wisconsin": "WI", "colorado": "CO",
        "minnesota": "MN", "south carolina": "SC", "alabama": "AL", "louisiana": "LA",
        "kentucky": "KY", "oregon": "OR", "oklahoma": "OK", "connecticut": "CT",
        "iowa": "IA", "mississippi": "MS", "arkansas": "AR", "kansas": "KS",
        "utah": "UT", "nevada": "NV", "new mexico": "NM", "nebraska": "NE",
        "west virginia": "WV", "idaho": "ID", "hawaii": "HI", "new hampshire": "NH",
        "maine": "ME", "montana": "MT", "rhode island": "RI", "delaware": "DE",
        "south dakota": "SD", "north dakota": "ND", "alaska": "AK", "vermont": "VT",
        "wyoming": "WY", "north carolina": "NC",
    }
    for state_name, code in state_map.items():
        if state_name in jurisdiction_lower:
            return code
    return None


# =========================================================================
# MedMal Damage Caps — Jurisdiction-Aware Settlement Adjustments
# =========================================================================

@router.get("/settlement/caps")
async def get_all_damage_caps():
    """Get medical malpractice damage caps for all 50 states + DC."""
    return damage_caps_utils.get_all_damage_caps()


@router.get("/settlement/caps/{state_code}")
async def get_state_damage_cap(state_code: str):
    """Get damage cap details for a specific state (e.g. 'CA', 'TX')."""
    cap = damage_caps_utils.get_damage_cap(state_code.upper())
    if not cap:
        raise HTTPException(404, detail=f"State '{state_code}' not found. Use 2-letter state code.")
    return cap.to_dict()


@router.post("/settlement/calculate-cap")
async def calculate_capped_payout(
    state_code: str,
    non_economic: float = 0.0,
    economic: float = 0.0,
):
    """
    Calculate maximum potential payout considering state damage caps.
    
    - state_code: Two-letter state abbreviation (e.g. 'CA', 'TX', 'NY')
    - non_economic: Estimated non-economic damages (pain & suffering)
    - economic: Estimated economic damages (medical bills, lost wages)
    
    Returns original vs. capped values with detailed breakdown.
    """
    return damage_caps_utils.calculate_capped_value(state_code.upper(), non_economic, economic)


@router.get("/settlement/caps/no-cap-states")
async def get_states_without_caps():
    """Get list of states with no effective damage caps (most favorable for plaintiffs)."""
    return damage_caps_utils.get_states_without_caps()


@router.get("/settlement/caps/cap-states")
async def get_states_with_caps():
    """Get list of states with active damage caps and their limits."""
    return damage_caps_utils.get_states_with_caps()


# =========================================================================
# 3. DepoLens™ — Deposition Intelligence
# =========================================================================

MOCK_DEPOSITIONS = [
    {
        "id": "dp-001",
        "deponent": "Dr. Sarah Mitchell",
        "role": "Defense Expert – Orthopedic Surgeon",
        "case_name": "Martinez v. St. Mary's Medical Center",
        "duration_minutes": 187,
        "transcript_pages": 94,
        "key_admissions": [
            "Admitted post-op notes were completed 72 hours after surgery (violates hospital policy)",
            "Acknowledged that standard of care requires sponge count before closing",
            "Could not identify who performed the final sponge count",
        ],
        "contradictions_with_prior_testimony": 7,
        "credibility_score": 63.2,
        "critical_highlights": [
            {"timestamp": "00:42:15", "text": "Q: Did you personally verify the sponge count? A: I relied on the nursing staff for that.", "severity": "high"},
            {"timestamp": "01:15:30", "text": "Q: When did you first learn of the retained sponge? A: Approximately 48 hours post-op.", "severity": "high"},
            {"timestamp": "01:52:00", "text": "Q: Have you changed your surgical protocol since this incident? A: No.", "severity": "medium"},
        ],
        "ai_generated_questions": [
            "If you relied on nursing staff for sponge count, what training did they receive?",
            "Why were post-op notes delayed by 72 hours?",
            "Have you reviewed the revised hospital policy on surgical counts?",
        ],
    },
    {
        "id": "dp-002",
        "deponent": "Nurse Jennifer Walsh",
        "role": "Defense Witness – OR Nurse",
        "case_name": "Martinez v. St. Mary's Medical Center",
        "duration_minutes": 145,
        "transcript_pages": 72,
        "key_admissions": [
            "Admitted she was covering two ORs simultaneously during the procedure",
            "Stated that the count sheet was not signed by a second nurse",
        ],
        "contradictions_with_prior_testimony": 3,
        "credibility_score": 71.8,
        "critical_highlights": [
            {"timestamp": "00:28:40", "text": "Q: How many ORs were you assigned to? A: Two. That's normal for our shift.", "severity": "high"},
        ],
        "ai_generated_questions": [
            "What is the maximum number of ORs a nurse should cover per hospital policy?",
        ],
    },
]


@router.get("/depolens/overview")
async def get_depolens_overview():
    """Get overview of all DepoLens™ deposition analyses."""
    return {
        "total_depositions_analyzed": len(MOCK_DEPOSITIONS),
        "total_hours_of_footage": round(sum(d["duration_minutes"] for d in MOCK_DEPOSITIONS) / 60, 1),
        "key_admissions_found": sum(len(d["key_admissions"]) for d in MOCK_DEPOSITIONS),
        "contradictions_flagged": sum(d["contradictions_with_prior_testimony"] for d in MOCK_DEPOSITIONS),
        "depositions": [
            {
                "id": d["id"],
                "deponent": d["deponent"],
                "role": d["role"],
                "case_name": d["case_name"],
                "credibility_score": d["credibility_score"],
                "key_admissions_count": len(d["key_admissions"]),
            }
            for d in MOCK_DEPOSITIONS
        ],
    }


@router.get("/depolens/deposition/{deposition_id}")
async def get_depolens_deposition(deposition_id: str):
    """Get detailed deposition analysis."""
    for dep in MOCK_DEPOSITIONS:
        if dep["id"] == deposition_id:
            return dep
    raise HTTPException(404, detail=f"Deposition {deposition_id} not found")


# =========================================================================
# 4. Compliance-Shield™ — HIPAA/Regulatory Compliance
# =========================================================================

MOCK_COMPLIANCE_REPORTS = [
    {
        "id": "cs-001",
        "firm_name": "Smith & Associates, P.C.",
        "report_period": "2026-05",
        "overall_score": 94.2,
        "status": "compliant",
        "checks_performed": 24,
        "checks_passed": 23,
        "checks_failed": 1,
        "critical_findings": 0,
        "findings": [
            {
                "check": "BAA on file with all cloud providers",
                "status": "passed",
                "details": "AWS, OpenAI, and Twilio BAAs verified current",
            },
            {
                "check": "AES-256 encryption enabled on PHI databases",
                "status": "passed",
                "details": "SQLite WAL mode + encryption verified",
            },
            {
                "check": "TLS 1.2+ enforced on all API endpoints",
                "status": "passed",
                "details": "All endpoints enforce HTTPS with TLS 1.3",
            },
            {
                "check": "Access logs review (30-day period)",
                "status": "passed",
                "details": "No unauthorized access detected",
            },
            {
                "check": "15-minute session timeout configured",
                "status": "failed",
                "details": "Current timeout set to 30 minutes — update recommended",
            },
        ],
        "last_audit_date": "2026-05-28",
        "next_audit_date": "2026-11-28",
    },
    {
        "id": "cs-002",
        "firm_name": "Johnson MedMal Law Group",
        "report_period": "2026-05",
        "overall_score": 88.7,
        "status": "attention_needed",
        "checks_performed": 24,
        "checks_passed": 21,
        "checks_failed": 3,
        "critical_findings": 1,
        "findings": [
            {
                "check": "BAA on file with all cloud providers",
                "status": "failed",
                "details": "OpenAI BAA missing — action required within 30 days",
            },
            {
                "check": "Staff HIPAA training (annual)",
                "status": "failed",
                "details": "3 staff members out of compliance — training overdue",
            },
            {
                "check": "PHI access audit trail complete",
                "status": "passed",
                "details": "7,342 events logged, no anomalies detected",
            },
        ],
        "last_audit_date": "2026-05-15",
        "next_audit_date": "2026-06-15",
    },
]


@router.get("/compliance/overview")
async def get_compliance_overview():
    """Get overview of Compliance-Shield™ for all firms."""
    return {
        "total_firms_monitored": len(MOCK_COMPLIANCE_REPORTS),
        "average_score": round(sum(r["overall_score"] for r in MOCK_COMPLIANCE_REPORTS) / len(MOCK_COMPLIANCE_REPORTS), 1),
        "compliant_firms": sum(1 for r in MOCK_COMPLIANCE_REPORTS if r["status"] == "compliant"),
        "attention_needed": sum(1 for r in MOCK_COMPLIANCE_REPORTS if r["status"] == "attention_needed"),
        "critical_findings_total": sum(r["critical_findings"] for r in MOCK_COMPLIANCE_REPORTS),
        "reports": [
            {
                "id": r["id"],
                "firm_name": r["firm_name"],
                "report_period": r["report_period"],
                "overall_score": r["overall_score"],
                "status": r["status"],
                "critical_findings": r["critical_findings"],
            }
            for r in MOCK_COMPLIANCE_REPORTS
        ],
    }


@router.get("/compliance/report/{report_id}")
async def get_compliance_report(report_id: str):
    """Get detailed compliance report."""
    for report in MOCK_COMPLIANCE_REPORTS:
        if report["id"] == report_id:
            return report
    raise HTTPException(404, detail=f"Compliance report {report_id} not found")


# =========================================================================
# Unified Enterprise Dashboard
# =========================================================================

@router.get("/dashboard")
async def get_enterprise_dashboard():
    """Get consolidated Enterprise dashboard data across all 4 modules."""
    return {
        "modules": {
            "discovery_vault": {
                "name": "Discovery-Vault™",
                "active_cases": len(MOCK_DISCOVERY_CASES),
                "documents_processed": sum(c["analyzed_documents"] for c in MOCK_DISCOVERY_CASES),
                "hours_saved": sum(c["review_hours_saved"] for c in MOCK_DISCOVERY_CASES),
            },
            "settlement_predictor": {
                "name": "Settlement-Predictor Pro™",
                "cases_analyzed": len(MOCK_SETTLEMENT_CASES),
                "total_value_analyzed": sum(c["demand_amount"] for c in MOCK_SETTLEMENT_CASES),
                "average_confidence": round(sum(c["ai_confidence"] for c in MOCK_SETTLEMENT_CASES) / len(MOCK_SETTLEMENT_CASES), 1),
            },
            "depolens": {
                "name": "DepoLens™",
                "depositions_analyzed": len(MOCK_DEPOSITIONS),
                "total_hours": round(sum(d["duration_minutes"] for d in MOCK_DEPOSITIONS) / 60, 1),
                "admissions_found": sum(len(d["key_admissions"]) for d in MOCK_DEPOSITIONS),
            },
            "compliance_shield": {
                "name": "Compliance-Shield™",
                "firms_monitored": len(MOCK_COMPLIANCE_REPORTS),
                "overall_health_score": round(sum(r["overall_score"] for r in MOCK_COMPLIANCE_REPORTS) / len(MOCK_COMPLIANCE_REPORTS), 1),
                "critical_issues": sum(r["critical_findings"] for r in MOCK_COMPLIANCE_REPORTS),
            },
        },
        "last_updated": datetime.utcnow().isoformat() + "Z",
    }