#!/usr/bin/env python3
"""
Provision a sample attorney user for testing the login flow.
Creates a test firm 'LexiFlow Tech' with an attorney user.
"""
import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models, database
from database import SessionLocal, engine
from auth import hash_password

def provision_test_attorney():
    """Create a test firm and attorney user for login testing."""
    db = SessionLocal()
    try:
        # Ensure tables exist
        models.Base.metadata.create_all(bind=engine)
        
        # Check or create test firm
        firm = db.query(models.Firm).filter(models.Firm.slug == "lexiflow-tech").first()
        if not firm:
            firm = models.Firm(
                name="LexiFlow Tech",
                slug="lexiflow-tech",
                branding_colors=json.dumps({"primary": "#2563eb", "secondary": "#1e40af"}),
                plan_status="active",
                billing_tier="enterprise",
            )
            db.add(firm)
            db.flush()
            print(f"Created firm: {firm.name} ({firm.slug})")
        else:
            print(f"Firm already exists: {firm.name} ({firm.slug})")
        
        # Check or create attorney user
        email = "attorney@lexiflow.tech"
        existing = db.query(models.User).filter(models.User.email == email).first()
        if not existing:
            user = models.User(
                email=email,
                hashed_password=hash_password("TestPass123!"),
                full_name="Sarah Johnson",
                firm_id=firm.id,
                role="attorney",
                is_active=1,
            )
            db.add(user)
            db.flush()
            print(f"Created attorney user: {user.full_name} ({email})")
        else:
            print(f"Attorney user already exists: {existing.email}")
        
        # Also create an admin user for the firm
        admin_email = "admin@lexiflow.tech"
        admin = db.query(models.User).filter(models.User.email == admin_email).first()
        if not admin:
            user = models.User(
                email=admin_email,
                hashed_password=hash_password("AdminPass123!"),
                full_name="LexiFlow Tech Admin",
                firm_id=firm.id,
                role="admin",
                is_active=1,
            )
            db.add(user)
            db.flush()
            print(f"Created admin user: {user.full_name} ({admin_email})")
        else:
            print(f"Admin user already exists: {admin.email}")
        
        db.commit()
        print("\n=== TEST CREDENTIALS ===")
        print(f"Firm: LexiFlow Tech (slug: lexiflow-tech)")
        print(f"Attorney: attorney@lexiflow.tech / TestPass123!")
        print(f"Admin:    admin@lexiflow.tech / AdminPass123!")
        print("========================\n")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    provision_test_attorney()