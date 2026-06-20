#!/usr/bin/env python3
"""
LexiFlow Enterprise CRM Demo — Firm Onboarding Configuration Seed.

Creates or updates a demo firm with pre-configured CRM integration settings
for the NYC Bar Association presentation (July 7, 2026).

Usage:
    python3 scripts/seed_crm_demo_config.py
    
Environment:
    Must be run from the LexiFlow-Final root directory with the database available.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Ensure we can import from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from models import Base, Firm, User
from auth import hash_password


DEMO_FIRM = {
    "name": "Smith & Lacien, P.C.",
    "slug": "smith-lacien",
    "plan_status": "enterprise_trial",
    "billing_tier": "enterprise",
    "production_sync_enabled": 1,
    "trial_expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
    "api_config_json": json.dumps({
        # Filevine Configuration (Demo Mode — Placeholder keys)
        "filevine_api_key": "fv_demo_key_placeholder",
        "filevine_api_secret": "fv_demo_secret_placeholder",
        "filevine_session_id": "fv_demo_session_placeholder",
        "filevine_org_id": "org_smith_lacien_demo",
        
        # Clio Grow Configuration (Demo Mode — Placeholder)
        "clio_client_id": "clio_demo_client_id_placeholder",
        "clio_client_secret": "clio_demo_secret_placeholder",
        "clio_access_token": "clio_demo_token_placeholder",
        "clio_refresh_token": "clio_demo_refresh_placeholder",
        "clio_redirect_uri": "https://lexiflow.co/crm/clio/callback",
        
        # LeadDock Configuration
        "leaddock_api_key": "leaddock_demo_key_placeholder",
        
        # Sync Settings
        "sync_min_score": 70,
        "sync_targets": ["filevine", "clio", "leaddock"],
        "notify_on_sync": True,
        "notification_email": "intake@smith-lacien-demo.com",
    }),
    "branding_logo": "/branding/logo-icon.svg",
    "branding_colors": json.dumps({"primary": "#1a3a5c", "accent": "#c9a84c"}),
    "voice_enabled": 1,
    "voice_config_json": json.dumps({
        "provider": "vapi",
        "language": "en",
        "greeting": "Thank you for calling Smith & Lacien. I'm Lexi, your AI intake assistant. How can I help you today?"
    }),
    "email_enabled": 1,
    "email_config_json": json.dumps({
        "notify_new_lead": True,
        "notify_high_score": True,
        "daily_digest": True,
    }),
    "active_hours_json": json.dumps({
        "monday": {"start": "08:00", "end": "20:00"},
        "tuesday": {"start": "08:00", "end": "20:00"},
        "wednesday": {"start": "08:00", "end": "20:00"},
        "thursday": {"start": "08:00", "end": "20:00"},
        "friday": {"start": "08:00", "end": "18:00"},
        "saturday": {"start": "09:00", "end": "14:00"},
        "sunday": None,
    }),
    "stripe_customer_id": "cus_demo_smith_lacien",
    "stripe_subscription_id": "sub_demo_enterprise",
}

DEMO_ENTERPRISE_FIRM = {
    "name": "LexiFlow Tech Demo",
    "slug": "lexiflow-tech",
    "plan_status": "active",
    "billing_tier": "enterprise",
    "production_sync_enabled": 1,
    "trial_expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat(),
    "api_config_json": json.dumps({
        "filevine_api_key": "fv_lexiflow_demo_key",
        "filevine_api_secret": "fv_lexiflow_demo_secret",
        "filevine_session_id": "fv_lexiflow_demo_session",
        "filevine_org_id": "org_lexiflow_demo",
        "clio_client_id": "clio_lexiflow_demo_id",
        "clio_client_secret": "clio_lexiflow_demo_secret",
        "clio_access_token": "clio_lexiflow_demo_token",
        "clio_refresh_token": "clio_lexiflow_demo_refresh",
        "clio_redirect_uri": "https://lexiflow.co/crm/clio/callback",
        "leaddock_api_key": "ld_lexiflow_demo_key",
        "sync_min_score": 50,
        "sync_targets": ["filevine", "clio", "leaddock"],
        "notify_on_sync": True,
        "notification_email": "attorney@lexiflow.tech",
    }),
    "voice_enabled": 1,
    "email_enabled": 1,
    "stripe_customer_id": "cus_demo_lexiflow",
    "stripe_subscription_id": "sub_demo_lexiflow_ent",
}


def seed_firm_config(db, firm_config: dict) -> Firm:
    """Create or update a firm with the given configuration."""
    firm = db.query(Firm).filter(Firm.slug == firm_config["slug"]).first()
    
    if firm:
        print(f"  Updating existing firm: {firm_config['name']} (slug: {firm_config['slug']})")
        for key, value in firm_config.items():
            setattr(firm, key, value)
    else:
        print(f"  Creating new firm: {firm_config['name']} (slug: {firm_config['slug']})")
        firm = Firm(**firm_config)
        db.add(firm)
    
    db.flush()
    return firm


def main():
    print("=" * 60)
    print("LexiFlow Enterprise CRM Demo — Firm Onboarding Configuration")
    print("=" * 60)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Seed Smith & Lacien (Enterprise demo firm)
        print("\n[1/2] Seeding Smith & Lacien firm...")
        firm1 = seed_firm_config(db, DEMO_FIRM)
        print(f"  ✓ Firm ID: {firm1.id}")
        
        # Seed LexiFlow Tech Demo firm
        print("\n[2/2] Seeding LexiFlow Tech Demo firm...")
        firm2 = seed_firm_config(db, DEMO_ENTERPRISE_FIRM)
        print(f"  ✓ Firm ID: {firm2.id}")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("✓ Firm onboarding configuration complete!")
        print("=" * 60)
        print(f"\nConfigured Firms:")
        print(f"  1. {firm1.name} (slug: {firm1.slug})")
        print(f"     - Plan: {firm1.plan_status} / Tier: {firm1.billing_tier}")
        print(f"     - CRM Sync: {'Enabled' if firm1.production_sync_enabled else 'Disabled'}")
        print(f"     - API Config: Filevine + Clio + LeadDock configured")
        print(f"  2. {firm2.name} (slug: {firm2.slug})")
        print(f"     - Plan: {firm2.plan_status} / Tier: {firm2.billing_tier}")
        print(f"     - CRM Sync: {'Enabled' if firm2.production_sync_enabled else 'Disabled'}")
        print(f"     - API Config: Filevine + Clio + LeadDock configured")
        print(f"\nDemo CRM Sync Endpoint:")
        print(f"  POST /api/demo/crm-sync  (Form param: firm_slug=lexiflow-tech)")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()