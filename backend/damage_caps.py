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


# Comprehensive state data sourced from authoritative CSV research file
# Source: /home/team/shared/research/medmal-caps-2026.csv
STATE_DAMAGE_CAPS: Dict[str, DamageCap] = {
    "AL": DamageCap("Alabama", "AL", None, "No cap ($750k punitives max); $1.5M punitive cap ($500k small biz)",
                    punitive_cap=1500000.0, punitive_notes="$1.5M cap ($500k for small business) — Ala. Code § 6-5-546"),
    "AK": DamageCap("Alaska", "AK", 250000.0, "$250k ($500k if severe permanent impairment), $1M total (AS 09.17.010)",
                    total_cap=1000000.0, has_exceptions=True,
                    exception_notes="$500k if severe permanent physical impairment; no cap if informed consent not obtained"),
    "AZ": DamageCap("Arizona", "AZ", None, "No cap (caps eliminated in tort reform 2021)",
                    punitive_cap=None, punitive_notes="2x compensatory for non-economic — AZ Rev Stat § 12-562"),
    "AR": DamageCap("Arkansas", "AR", 500000.0, "$500k cap (indexed), $1M total (Ark. Code § 16-114-206)",
                    total_cap=1000000.0, exception_notes="Cap applies per occurrence, not per defendant"),
    "CA": DamageCap("California", "CA", 353000.0, "$353k cap (MICRA, indexed for 2026), $250k total only (CA Civ Code § 3333.1-2)",
                    punitive_cap=250000.0, punitive_notes="$250k or 3x compensatory — 3x punitive limit",
                    has_exceptions=True, exception_notes="MICRA reform 2022; indexed annually from $250k base"),
    "CO": DamageCap("Colorado", "CO", 1369200.0, "$1,369,200 cap (indexed annually), $1,369,200 total (C.R.S. § 13-21-102.5)",
                    total_cap=1369200.0, exception_notes="$300k limit on attorney fees capped separately"),
    "CT": DamageCap("Connecticut", "CT", None, "No cap on any damages (CT Gen Stat § 52-584)",
                    punitive_cap=None, punitive_notes="2x compensatory (cap $250k) — one of few states with no caps"),
    "DE": DamageCap("Delaware", "DE", 250000.0, "$250k to $1,223,670 sliding scale; $1M total (DE Code tit 18 § 6801-15)",
                    total_cap=1000000.0, has_exceptions=True,
                    exception_notes="$250k individual, $1.22M health system; punitives only for 'wanton' conduct"),
    "FL": DamageCap("Florida", "FL", None, "No cap (repealed 2017); 3x compensatory or $500k punitive (FL Stat § 766.201-212)",
                    punitive_cap=500000.0, punitive_notes="3x compensatory or $500k"),
    "GA": DamageCap("Georgia", "GA", None, "No cap on non-economic damages in med mal (GA Code § 51-12-5.1)",
                    punitive_cap=None, punitive_notes="No cap ($250k for product liability) — several liability"),
    "HI": DamageCap("Hawaii", "HI", 375000.0, "$375k cap (indexed for inflation), no total cap (HI Rev Stat § 671-3)",
                    has_exceptions=True, exception_notes="Waiver of cap required for informed consent"),
    "ID": DamageCap("Idaho", "ID", 250000.0, "$250k cap (non-indexed), $1M total (ID Code § 6-1603)",
                    total_cap=1000000.0, exception_notes="Among the strictest caps in the nation"),
    "IL": DamageCap("Illinois", "IL", None, "No cap (ruled unconstitutional 2010, Lebron v. Gottlieb)",
                    punitive_cap=None, punitive_notes="No cap — 735 ILCS 5/2-1115.1"),
    "IN": DamageCap("Indiana", "IN", None, "$1.8M total cap (indexed), comprehensive patient compensation fund (IN Code § 34-18-14-3)",
                    total_cap=1800000.0, citation="$250k from provider + $1.6M from fund",
                    exception_notes="Depends on availability of excess insurance"),
    "IA": DamageCap("Iowa", "IA", 250000.0, "$250k ($1M if substantial permanent loss), $1M total (IA Code § 147.140-147.146)",
                    total_cap=1000000.0, has_exceptions=True,
                    exception_notes="$1M cap applies for 'substantial' injuries"),
    "KS": DamageCap("Kansas", "KS", 250000.0, "$250k cap (increased 2014), no aggregate cap (KS Stat § 60-3407)",
                    punitive_cap=500000.0, punitive_notes="$500k or $250k (higher of)"),
    "KY": DamageCap("Kentucky", "KY", None, "No caps (1 yr statute) — one of few states with no caps",
                    punitive_cap=None, punitive_notes="No cap"),
    "LA": DamageCap("Louisiana", "LA", 500000.0, "$500k total cap (indexed) — patient compensation fund over $100k (LA Rev Stat § 40:1299.42)",
                    total_cap=500000.0, punitive_cap=250000.0, punitive_notes="$250k or 2x compensatory"),
    "ME": DamageCap("Maine", "ME", 400000.0, "$400k cap (indexed biennially), $400k total (ME Rev Stat tit 24 § 2902)",
                    total_cap=400000.0, punitive_cap=None, punitive_notes="No cap"),
    "MD": DamageCap("Maryland", "MD", 890000.0, "$890k cap (indexed for 2026), $890k total (MD Cts & Jud Pro Code § 3-2A-09)",
                    total_cap=890000.0, has_exceptions=True,
                    exception_notes="Wrongful death has separate cap schedule; increased annually by CPI"),
    "MA": DamageCap("Massachusetts", "MA", None, "No cap — only cap is on total non-economic damages ($500k total) (MGL c. 231 § 60H)",
                    total_cap=500000.0, punitive_cap=None, punitive_notes="No cap"),
    "MI": DamageCap("Michigan", "MI", 789100.0, "$789,100 cap (indexed for 2026), $789.1k total (MI Comp Laws § 600.1483)",
                    total_cap=789100.0, has_exceptions=True,
                    exception_notes="Adjusted annually; higher cap for brain/spine injuries"),
    "MN": DamageCap("Minnesota", "MN", 400000.0, "$400k cap (indexed), $400k total (MN Stat § 549.26)",
                    total_cap=400000.0, punitive_cap=None, punitive_notes="No cap"),
    "MS": DamageCap("Mississippi", "MS", 1000000.0, "$1M (surgical), $500k (non-surgical) — $1M total (MS Code § 41-33-1 et seq)",
                    total_cap=1000000.0, has_exceptions=True,
                    exception_notes="Lower cap for non-surgical claims; no punitive caps for intentional acts"),
    "MO": DamageCap("Missouri", "MO", 484465.0, "$484,465 cap (indexed annually), $484.5k total (MO Rev Stat § 538.210)",
                    total_cap=484465.0, punitive_cap=500000.0,
                    punitive_notes="$500k for non-physical injury"),
    "MT": DamageCap("Montana", "MT", 250000.0, "$250k cap per defendant, no total cap (MT Code § 25-9-411)",
                    punitive_cap=250000.0, punitive_notes="$250k or 3x economic"),
    "NE": DamageCap("Nebraska", "NE", 1750000.0, "$1.75M cap (indexed from $250k in 1976), $1.75M total (NE Rev Stat § 44-2825)",
                    total_cap=1750000.0, has_exceptions=True,
                    exception_notes="$2.25M for catastrophic injuries; oldest med mal cap (1976)"),
    "NV": DamageCap("Nevada", "NV", 350000.0, "$350k per defendant, no total cap (NV Rev Stat § 41A-035)",
                    punitive_cap=300000.0, punitive_notes="$300k cap for small business; 3x compensatory"),
    "NH": DamageCap("New Hampshire", "NH", 250000.0, "$250k ($500k catastrophic), $250k per provider (NH Rev Stat § 507-C:2)",
                    has_exceptions=True, exception_notes="$500k for catastrophic injuries (limited)"),
    "NJ": DamageCap("New Jersey", "NJ", None, "No cap on med mal non-economic damages (NJ Stat § 2A:53A-29)",
                    punitive_cap=350000.0, punitive_notes="$350k cap for non-physical injury"),
    "NM": DamageCap("New Mexico", "NM", 750000.0, "$750k total cap (indexed), $750k total (NM Stat § 41-5-6)",
                    total_cap=750000.0, punitive_cap=500000.0, punitive_notes="$500k or 3x compensatory"),
    "NY": DamageCap("New York", "NY", None, "No cap on non-economic damages in med mal (NY CPLR § 214-a, § 3017)",
                    punitive_cap=None, punitive_notes="No cap (cap only for med mal?)"),
    "NC": DamageCap("North Carolina", "NC", 575000.0, "$500k cap (indexed to $575k 2026), $500k total (NC Gen Stat § 90-21.19)",
                    total_cap=575000.0, punitive_cap=250000.0, punitive_notes="$250k for negligence"),
    "ND": DamageCap("North Dakota", "ND", 500000.0, "$500k per defendant, no total cap (ND Cent Code § 32-42-02)",
                    punitive_cap=250000.0, punitive_notes="$250k or 2x compensatory"),
    "OH": DamageCap("Ohio", "OH", 250000.0, "$250k per plaintiff ($500k catastrophic), $1M total ($1.5M catastrophic) (OH Rev Stat § 2323.43)",
                    total_cap=1000000.0, has_exceptions=True,
                    exception_notes="$1.5M for catastrophic; 2x compensatory punitive (cap $250k)"),
    "OK": DamageCap("Oklahoma", "OK", 1300000.0, "$750k cap (indexed to $1.3M 2026), $1.3M total (OK Stat tit 63 § 1-1708.1E)",
                    total_cap=1300000.0, exception_notes="Struck down 2019, reinstated 2020"),
    "OR": DamageCap("Oregon", "OR", 500000.0, "$500k cap, $500k total (OR Rev Stat § 31.710)",
                    total_cap=500000.0, punitive_cap=200000.0, punitive_notes="$200k for non-physical"),
    "PA": DamageCap("Pennsylvania", "PA", None, "No cap (struck down 2006 by PA Supreme Court) (42 PA Cons Stat § 5138)",
                    punitive_cap=None, punitive_notes="No cap"),
    "RI": DamageCap("Rhode Island", "RI", None, "No statutory caps on med mal (RI Gen Laws § 9-19-26)",
                    punitive_cap=250000.0, punitive_notes="$250k cap for negligence"),
    "SC": DamageCap("South Carolina", "SC", 509200.0, "$509,200 cap (indexed from 2005), $509.2k total (SC Code § 15-32-220)",
                    total_cap=509200.0, punitive_cap=None, punitive_notes="No cap"),
    "SD": DamageCap("South Dakota", "SD", 500000.0, "$500k cap, $500k total (SD Cod Laws § 21-3-11)",
                    total_cap=500000.0, punitive_cap=None, punitive_notes="No cap"),
    "TN": DamageCap("Tennessee", "TN", 750000.0, "$750k ($1.25M total) — facility liability limit $250k (TN Code § 29-26-119)",
                    total_cap=1250000.0, punitive_cap=500000.0,
                    punitive_notes="$500k for non-mal practice"),
    "TX": DamageCap("Texas", "TX", 250000.0, "$250k per defendant, $750k total max (TX Civ Prac & Rem Code § 74.301)",
                    total_cap=750000.0, punitive_cap=250000.0,
                    punitive_notes="$250k or 2x compensatory"),
    "UT": DamageCap("Utah", "UT", 500000.0, "$450k cap (indexed to $500k 2026), $1M total (UT Code § 78B-3-410)",
                    total_cap=1000000.0, punitive_cap=500000.0,
                    punitive_notes="$500k for non-medical"),
    "VT": DamageCap("Vermont", "VT", None, "No medical malpractice damage caps (3 yrs statute)",
                    punitive_cap=None, punitive_notes="No cap"),
    "VA": DamageCap("Virginia", "VA", 3450000.0, "$3M cap (indexed to $3.45M 2026), $3.45M total (VA Code § 8.01-581.15)",
                    total_cap=3450000.0, punitive_cap=500000.0,
                    punitive_notes="$500k for non-physical; highest cap in the nation"),
    "WA": DamageCap("Washington", "WA", None, "No caps on med mal damages (Supreme Ct ruled 1989) (WA Rev Code § 4.56.250)",
                    punitive_cap=500000.0, punitive_notes="$500k cap for non-personal injury"),
    "WV": DamageCap("West Virginia", "WV", 500000.0, "$500k (unless death/permanent injury), $1M total (WV Code § 55-7B-8)",
                    total_cap=1000000.0, has_exceptions=True,
                    exception_notes="$500k cap but limited exceptions for death/permanent injury"),
    "WI": DamageCap("Wisconsin", "WI", 1185000.0, "$1.185M cap (indexed for 2026), $1.185M total (WI Stat § 893.55)",
                    total_cap=1185000.0, punitive_cap=200000.0,
                    punitive_notes="$200k for non-physical; one of highest caps; indexed annually"),
    "WY": DamageCap("Wyoming", "WY", 250000.0, "$250k total cap, $250k total (WY Stat § 1-1-112)",
                    total_cap=250000.0, punitive_cap=None, punitive_notes="No cap — per occurrence only; very limited"),
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