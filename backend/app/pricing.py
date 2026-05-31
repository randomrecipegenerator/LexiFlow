"""Pricing configuration for LexiFlow Legal Suite.

Flat-rate $69/mo subscription with usage-based fees for high-volume features.
"""

SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic",
        "monthly_price": 69.0,
        "description": "Complete LexiFlow Suite — all 6 modules",
        "features": [
            "AI Intake Agent (unlimited leads)",
            "Voice AI Receptionist (500 min/month)",
            "AI Medical Chronologies (10 docs/month)",
            "Auto-Document Drafter (10 docs/month)",
            "DepoLens AI (5 analyses/month)",
            "Settlement Estimator (unlimited)",
            "Email support",
            "HIPAA-compliant storage",
        ],
    },
    "advanced": {
        "name": "Advanced",
        "monthly_price": 149.0,
        "description": "Higher limits + priority support",
        "features": [
            "AI Intake Agent (unlimited leads)",
            "Voice AI Receptionist (2000 min/month)",
            "AI Medical Chronologies (50 docs/month)",
            "Auto-Document Drafter (50 docs/month)",
            "DepoLens AI (20 analyses/month)",
            "Priority support",
            "Custom CRM integration",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "monthly_price": 299.0,
        "description": "Unlimited everything with dedicated support",
        "features": [
            "All features unlimited",
            "Dedicated account manager",
            "99.9% uptime SLA",
            "SSO/SAML auth",
            "Audit logging",
        ],
    },
}

USAGE_FEES = [
    {"feature": "AI Medical Chronologies", "price": 5.0, "unit": "per document", "description": "Beyond-plan chronology docs"},
    {"feature": "OCR Processing", "price": 2.0, "unit": "per 100 pages", "description": "Scanned document OCR"},
    {"feature": "Voice AI Receptionist", "price": 0.10, "unit": "per minute", "description": "Additional voice minutes"},
    {"feature": "Auto-Document Drafter", "price": 3.0, "unit": "per document", "description": "Additional drafted docs"},
]

INTEGRATION_FEES = [
    {"provider": "filevine", "setup": 0, "monthly": 0, "description": "Included in all plans"},
    {"provider": "clio", "setup": 0, "monthly": 0, "description": "Included in all plans"},
    {"provider": "leaddock", "setup": 0, "monthly": 0, "description": "Included in all plans"},
    {"provider": "salesforce", "setup": 500, "monthly": 99, "description": "Enterprise add-on"},
]

COMPETITOR_PRICES = {
    "LexiFlow Basic": 69,
    "LexiFlow Advanced": 149,
    "LexiFlow Enterprise": 299,
    "Clio Grow": 399,
    "Filevine": 499,
    "LawRuler": 299,
    "Traditional Paralegal": 4000,
}

SAVINGS_MESSAGE = "Replace $1,000+/mo tools with LexiFlow for just $69/mo. Save 93%."