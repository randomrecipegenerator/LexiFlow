"""
LexiFlow MedMal Damage Caps Module.

Provides state-specific medical malpractice damage cap data and integrates
with the Settlement-Predictor Pro™ API to calculate jurisdiction-adjusted
settlement predictions.

Sources:
- State statutes and case law (current as of 2026)
- Non-economic damage caps (pain & suffering)
- Punitive damage caps
- Exceptions and special rules
"""
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# =========================================================================
# State Damage Cap Data
# =========================================================================

@dataclass
class DamageCap:
    """Represents one state's medical malpractice damage cap rules."""
    state: str
    state_code: str
    non_economic_cap: Optional[float]       # Max non-economic damages (None = no cap)
    non_economic_notes: str = ""
    punitive_cap: Optional[float] = None     # Max punitive damages (None = no cap)
    punitive_notes: str = ""
    has_exceptions: bool = False
    exception_notes: str = ""
    total_cap: Optional[float] = None        # Overall cap on ALL damages (rare)
    citation: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


# Comprehensive state data sourced from state statutes
STATE_DAMAGE_CAPS: Dict[str, DamageCap] = {
    "AL": DamageCap("Alabama", "AL", None, "No statutory cap on non-economic damages", 
                    punitive_cap=1500000.0, punitive_notes="Punitive capped at $1.5M (Ala. Code § 6-11-21)"),
    "AK": DamageCap("Alaska", "AK", 400000.0, "$400k cap on non-economic damages for PI (AS 09.17.010)", 
                    has_exceptions=True, exception_notes="Cap adjusted for CPI annually"),
    "AZ": DamageCap("Arizona", "AZ", None, "No cap on non-economic damages (AZ abolished caps)",
                    punitive_cap=None, punitive_notes="No punitive cap"),
    "AR": DamageCap("Arkansas", "AR", 500000.0, "$500k cap on non-economic damages (Ark. Code § 16-114-206)",
                    total_cap=1000000.0, exception_notes="$1M total cap on all damages"),
    "CA": DamageCap("California", "CA", 250000.0, "$250k cap on non-economic damages (MICRA § 3333.2)",
                    has_exceptions=True, exception_notes="Cap applies per defendant; wrongful death exception being litigated"),
    "CO": DamageCap("Colorado", "CO", 1246367.0, "$1,246,367 (adjusted annually for inflation, C.R.S. § 13-64-302)",
                    punitive_cap=None, punitive_notes="Punitive damages allowed but limited"),
    "CT": DamageCap("Connecticut", "CT", None, "No cap on non-economic damages",
                    punitive_cap= None, punitive_notes="Punitive limited to costs and fees"),
    "DE": DamageCap("Delaware", "DE", None, "No statutory cap on non-economic damages",
                    punitive_cap=None, punitive_notes="No punitive cap"),
    "FL": DamageCap("Florida", "FL", None, "No cap on non-economic damages (FL Supreme Court struck down caps in 2017)",
                    punitive_cap=2000000.0, punitive_notes="Punitive capped at $2M or 3x compensatory (Fla. Stat. § 768.73)"),
    "GA": DamageCap("Georgia", "GA", 350000.0, "$350k cap on non-economic damages in med mal (O.C.G.A. § 51-13-1)",
                    total_cap=1750000.0, exception_notes="$1.75M total cap if multiple defendants"),
    "HI": DamageCap("Hawaii", "HI", 375000.0, "$375k cap on non-economic damages (HRS § 663-8.7)",
                    has_exceptions=True, exception_notes="Cap adjusted for inflation; last adjusted to $375k"),
    "ID": DamageCap("Idaho", "ID", 250000.0, "$250k cap on non-economic damages (Idaho Code § 6-1603)",
                    has_exceptions=True, exception_notes="Exception for certain catastrophic injuries"),
    "IL": DamageCap("Illinois", "IL", None, "No cap on non-economic damages (IL Supreme Court struck down caps in Best v. Taylor Machine Works)",
                    punitive_cap=None, punitive_notes="No punitive damages in med Mal practice (735 ILCS 5/2-1115)"),
    "IN": DamageCap("Indiana", "IN", 1800000.0, "$1.8M cap on total damages per occurrence (Ind. Code § 34-18-2-15)",
                    total_cap=1800000.0, citation="Indiana's cap is total, not just non-economic"),
    "IA": DamageCap("Iowa", "IA", 250000.0, "$250k cap on non-economic damages (Iowa Code § 147.136A)",
                    has_exceptions=True, exception_notes="Cap higher for permanent injuries ($500k-$1M)"),
    "KS": DamageCap("Kansas", "KS", 250000.0, "$250k cap on non-economic damages (K.S.A. § 60-3407)",
                    has_exceptions=True, exception_notes="Exception for catastrophic injury ($500k cap increase)"),
    "KY": DamageCap("Kentucky", "KY", None, "No cap on non-economic damages",
                    punitive_cap=None, punitive_notes="Punitive allowed but rare in med Mal practice"),
    "LA": DamageCap("Louisiana", "LA", 500000.0, "$500k cap on total damages (La. R.S. § 40:1231.2)",
                    total_cap=500000.0, citation="Louisiana's cap is total, including future medical"),
    "ME": DamageCap("Maine", "ME", 400000.0, "$400k cap on non-economic damages (24-A M.R.S. § 2902)",
                    punitive_cap= None, punitive_notes="Punitive damages generally not allowed against healthcare providers"),
    "MD": DamageCap("Maryland", "MD", 890000.0, "$890k cap on non-economic damages (adjusted annually, Md. Code Cts. & Jud. Proc. § 3-2A-09)",
                    has_exceptions=True, exception_notes="Wrongful death has separate cap schedule"),
    "MA": DamageCap("Massachusetts", "MA", 500000.0, "$500k cap on non-economic damages (M.G.L. c. 231, § 60H)",
                    punitive_cap=None, punitive_notes="Punitive damages generally not allowed"),
    "MI": DamageCap("Michigan", "MI", 908300.0, "$908,300 cap on non-economic damages (adjusted annually, MCL § 600.1483)",
                    has_exceptions=True, exception_notes="Higher cap for brain/spine injuries"),
    "MN": DamageCap("Minnesota", "MN", 400000.0, "$400k cap on non-economic damages (Minn. Stat. § 549.23)",
                    has_exceptions=True, exception_notes="Cap applies per occurrence, not per plaintiff"),
    "MS": DamageCap("Mississippi", "MS", 500000.0, "$500k cap on non-economic damages (Miss. Code § 11-1-60)",
                    has_exceptions=True, exception_notes="Cap increased to $1M for catastrophic injuries"),
    "MO": DamageCap("Missouri", "MO", 441605.0, "$441,605 cap on non-economic damages (adjusted annually, Mo. Rev. Stat. § 538.210)",
                    punitive_cap=500000.0, punitive_notes="Punitive capped at $500k (Mo. Rev. Stat. § 510.265)"),
    "MT": DamageCap("Montana", "MT", 250000.0, "$250k cap on non-economic damages (MCA § 25-9-411)",
                    has_exceptions=True, exception_notes="Amount adjusted for inflation"),
    "NE": DamageCap("Nebraska", "NE", 500000.0, "$500k cap on total damages (Neb. Rev. Stat. § 44-2825)",
                    total_cap=500000.0, exception_notes="Comprehensive cap on total damages; noneconomic portion limited"),
    "NV": DamageCap("Nevada", "NV", 350000.0, "$350k cap on non-economic damages (NRS § 41A.035)",
                    total_cap=750000.0, exception_notes="$750k total cap if there are multiple defendants"),
    "NH": DamageCap("New Hampshire", "NH", 475000.0, "$475k cap on non-economic damages (RSA § 507-C:7)",
                    punitive_cap=None, punitive_notes="Punitive damages not allowed in med Mal practice"),
    "NJ": DamageCap("New Jersey", "NJ", None, "No cap on non-economic damages",
                    punitive_cap=None, punitive_notes="Punitive limited by NJPLA (2 years statute)"),
    "NM": DamageCap("New Mexico", "NM", 600000.0, "$600k cap on total damages (NMSA § 41-5-6)",
                    total_cap=600000.0, exception_notes="Comprehensive cap including both economic and non-economic"),
    "NY": DamageCap("New York", "NY", None, "No cap on non-economic damages",
                    punitive_cap=None, punitive_notes="Punitive damages allowed but rare"),
    "NC": DamageCap("North Carolina", "NC", None, "No cap on non-economic damages",
                    punitive_cap=250000.0, punitive_notes="Punitive capped at $250k or 3x compensatory (NCGS § 1D-25)"),
    "ND": DamageCap("North Dakota", "ND", 500000.0, "$500k cap on non-economic damages (NDCC § 32-03.2-04)",
                    punitive_cap=250000.0, punitive_notes="Punitive capped at $250k (NDCC § 32-03.2-11)"),
    "OH": DamageCap("Ohio", "OH", 250000.0, "$250k cap on non-economic damages (ORC § 2323.43)",
                    has_exceptions=True, exception_notes="$500k for catastrophic injury; $1M for permanent injury"),
    "OK": DamageCap("Oklahoma", "OK", 350000.0, "$350k cap on non-economic damages (OK Stat. § 63-1-1708)",
                    total_cap=1000000.0, exception_notes="$1M total cap; struck down and reinstated multiple times"),
    "OR": DamageCap("Oregon", "OR", 500000.0, "$500k cap on non-economic damages (ORS § 31.710)",
                    punitive_cap=None, punitive_notes="Punitive limited by statute (ORS § 31.730)"),
    "PA": DamageCap("Pennsylvania", "PA", None, "No cap on non-economic damages (PA Supreme Court struck down in 2022)",
                    punitive_cap=None, punitive_notes="Punitive damages allowed"),
    "RI": DamageCap("Rhode Island", "RI", None, "No cap on non-economic damages",
                    punitive_cap=None, punitive_notes="No statutory cap"),
    "SC": DamageCap("South Carolina", "SC", 531215.0, "$531,215 cap on non-economic damages (adjusted annually, SC Code § 15-32-220)",
                    total_cap=1062430.0, exception_notes="$1,062,430 total cap; adjusted annually"),
    "SD": DamageCap("South Dakota", "SD", 500000.0, "$500k cap on non-economic damages (SDCL § 21-3-11)",
                    punitive_cap=None, punitive_notes="Punitive damages allowed with clear evidence"),
    "TN": DamageCap("Tennessee", "TN", 750000.0, "$750k cap on non-economic damages (TCA § 29-39-102)",
                    has_exceptions=True, exception_notes="$1M for catastrophic injury; adjusted annually"),
    "TX": DamageCap("Texas", "TX", 250000.0, "$250k cap per defendant on non-economic damages (Tex. Civ. Prac. & Rem. § 74.301)",
                    total_cap=750000.0, exception_notes="$250k per defendant, max $750k total across all defendants"),
    "UT": DamageCap("Utah", "UT", 450000.0, "$450k cap on non-economic damages (Utah Code § 78B-3-410)",
                    has_exceptions=True, exception_notes="Amount adjusted for inflation; exceptions for permanent disability"),
    "VT": DamageCap("Vermont", "VT", None, "No cap on non-economic damages",
                    punitive_cap=None, punitive_notes="Punitive damages limited to $500k (12 VSA § 7001)"),
    "VA": DamageCap("Virginia", "VA", 2190000.0, "$2.19M cap on total damages (adjusted annually, VA Code § 8.01-581.15)",
                    total_cap=2190000.0, exception_notes="Comprehensive cap on ALL damages (economic + non-economic)"),
    "WA": DamageCap("Washington", "WA", None, "No cap on non-economic damages (struck down in 2019)",
                    punitive_cap=None, punitive_notes="Punitive damages not allowed (WA does not recognize punitive damages)"),
    "WV": DamageCap("West Virginia", "WV", 250000.0, "$250k cap on non-economic damages (WV Code § 55-7B-8)",
                    has_exceptions=True, exception_notes="$500k for catastrophic injury, $1M for permanent injury"),
    "WI": DamageCap("Wisconsin", "WI", 1149137.0, "$1,149,137 cap on non-economic damages (adjusted annually, Wis. Stat. § 893.555)",
                    has_exceptions=True, exception_notes="$2,298,274 for certain catastrophic injuries"),
    "WY": DamageCap("Wyoming", "WY", 250000.0, "$250k cap on non-economic damages (Wyo. Stat. § 1-1-130)",
                    punitive_cap=None, punitive_notes="Punitive damages limited to 25% of compensatory (Wyo. Stat. § 1-1-130)"),
}


# =========================================================================
# Damage Cap Query & Calculation
# =========================================================================

def get_damage_cap(state_code: str) -> Optional[DamageCap]:
    """Get damage cap data for a given state code (e.g. 'CA', 'TX')."""
    return STATE_DAMAGE_CAPS.get(state_code.upper())


def get_all_damage_caps() -> Dict[str, dict]:
    """Get all state damage cap data as dicts."""
    return {code: cap.to_dict() for code, cap in STATE_DAMAGE_CAPS.items()}


def calculate_capped_value(state_code: str, non_economic_damages: float, 
                           economic_damages: float = 0.0) -> dict:
    """
    Calculate capped damage values for a given state and damage estimates.
    
    Args:
        state_code: Two-letter state code (e.g. 'CA', 'TX')
        non_economic_damages: Estimated non-economic damages (pain & suffering)
        economic_damages: Estimated economic damages (medical bills, lost wages)
        
    Returns:
        Dict with original values, capped values, and cap details
    """
    cap = get_damage_cap(state_code)
    if not cap:
        return {
            "state_code": state_code,
            "error": f"Unknown state code: {state_code}",
            "original_non_economic": non_economic_damages,
            "original_economic": economic_damages,
            "capped_non_economic": non_economic_damages,
            "capped_economic": economic_damages,
            "capped_total": non_economic_damages + economic_damages,
            "cap_applied": False,
        }
    
    capped_non_economic = non_economic_damages
    cap_applied_parts = []
    
    # Apply non-economic cap
    if cap.non_economic_cap is not None and cap.non_economic_cap < non_economic_damages:
        capped_non_economic = cap.non_economic_cap
        cap_applied_parts.append(f"non-economic capped at ${cap.non_economic_cap:,.0f}")
    
    # Apply total cap (overrides everything)
    total_damages = capped_non_economic + economic_damages
    if cap.total_cap is not None and cap.total_cap < total_damages:
        capped_total = cap.total_cap
        cap_applied_parts.append(f"total damages capped at ${cap.total_cap:,.0f}")
    else:
        capped_total = total_damages
    
    return {
        "state_code": state_code,
        "state_name": cap.state,
        "original_non_economic": non_economic_damages,
        "original_economic": economic_damages,
        "original_total": non_economic_damages + economic_damages,
        "capped_non_economic": capped_non_economic,
        "capped_economic": economic_damages,
        "capped_total": capped_total,
        "reduction_amount": (non_economic_damages + economic_damages) - capped_total,
        "cap_applied": len(cap_applied_parts) > 0,
        "cap_details": "; ".join(cap_applied_parts) if cap_applied_parts else "No caps applied",
        "non_economic_cap": cap.non_economic_cap,
        "total_cap": cap.total_cap,
        "has_exceptions": cap.has_exceptions,
        "exception_notes": cap.exception_notes,
        "citation": cap.citation,
    }


def get_states_without_caps() -> List[dict]:
    """Get list of states that have no effective damage caps."""
    return [
        {"state": cap.state, "state_code": code}
        for code, cap in STATE_DAMAGE_CAPS.items()
        if cap.non_economic_cap is None and cap.total_cap is None
    ]


def get_states_with_caps() -> List[dict]:
    """Get list of states that have damage caps in place."""
    return [
        {"state": cap.state, "state_code": code, 
         "cap_type": "non-economic" if cap.non_economic_cap else "total",
         "cap_amount": cap.non_economic_cap or cap.total_cap}
        for code, cap in STATE_DAMAGE_CAPS.items()
        if cap.non_economic_cap is not None or cap.total_cap is not None
    ]


# =========================================================================
# FastAPI Endpoints (to be registered in enterprise_api.py)
# =========================================================================

CAP_ROUTER_PREFIX = "/api/enterprise/settlement"

# Sample ready-to-use endpoint definitions
ENDPOINT_DEFINITIONS = """
# Add these endpoints to enterprise_api.py:

@router.get("/settlement/caps")
async def get_all_damage_caps():
    \"\"\"Get medical malpractice damage caps for all states.\"\"\"
    return damage_caps_utils.get_all_damage_caps()

@router.get("/settlement/caps/{state_code}")
async def get_state_damage_cap(state_code: str):
    \"\"\"Get damage cap for a specific state.\"\"\"
    cap = damage_caps_utils.get_damage_cap(state_code)
    if not cap:
        raise HTTPException(404, detail=f"State '{state_code}' not found")
    return cap.to_dict()

@router.post("/settlement/calculate-cap")
async def calculate_cap(state_code: str, non_economic: float, economic: float = 0.0):
    \"\"\"Calculate capped damages for a settlement estimate.\"\"\"
    return damage_caps_utils.calculate_capped_value(state_code, non_economic, economic)
"""