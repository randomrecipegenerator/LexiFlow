import os
import sys
import json
import argparse
from sqlalchemy.orm import Session

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend import models, database, ai_engine
from backend.database import SessionLocal, engine

def provision_firm(name: str, slug: str, email: str, password: str, branding_json_path: str = None, criteria_text: str = None, criteria_url: str = None):
    db = SessionLocal()
    try:
        # Check if firm already exists
        existing_firm = db.query(models.Firm).filter(models.Firm.slug == slug).first()
        
        branding_logo = None
        branding_colors = json.dumps({
            "primary": "#2563eb",
            "secondary": "#1e40af"
        })
        
        if branding_json_path and os.path.exists(branding_json_path):
            with open(branding_json_path, 'r') as f:
                config = json.load(f)
                if 'branding' in config:
                    branding = config['branding']
                    branding_logo = branding.get('logo')
                    branding_colors = json.dumps(branding.get('colors', {}))
                if 'firm_name' in config:
                    name = config['firm_name']

        if existing_firm:
            print(f"Firm with slug '{slug}' already exists. Updating...")
            firm = existing_firm
            firm.name = name
            firm.branding_logo = branding_logo
            firm.branding_colors = branding_colors
        else:
            # Create firm
            firm = models.Firm(
                name=name,
                slug=slug,
                branding_logo=branding_logo,
                branding_colors=branding_colors
            )
            db.add(firm)
        
        db.flush()

        # Create admin user if not exists
        existing_user = db.query(models.User).filter(models.User.email == email).first()
        if not existing_user:
            user = models.User(
                email=email,
                hashed_password=password, # In a real app, hash this!
                full_name=f"{name} Admin",
                firm_id=firm.id,
                role="admin"
            )
            db.add(user)
        
        # Generate custom qualification rules if criteria provided
        qualification_rules = f"Identify if this is a high-value case for {name}."
        
        input_criteria = criteria_text
        if criteria_url:
            print(f"Fetching criteria from {criteria_url}...")
            try:
                import httpx
                resp = httpx.get(criteria_url, follow_redirects=True, timeout=10.0)
                input_criteria = f"Content from {criteria_url}:\n\n{resp.text[:10000]}"
            except Exception as e:
                print(f"Warning: Failed to fetch criteria URL: {e}")
        
        if input_criteria:
            print("Generating AI-powered qualification rules...")
            qualification_rules = ai_engine.generate_qualification_rules(name, input_criteria)

        # Create or update a default intake form
        form = db.query(models.Form).filter(models.Form.firm_id == firm.id, models.Form.name == "General Intake Form").first()
        if not form:
            form = models.Form(
                firm_id=firm.id,
                name="General Intake Form",
                qualification_rules=qualification_rules
            )
            db.add(form)
            db.flush()
            
            # Add default questions
            questions = [
                ("What is your full name?", "text", 0),
                ("What is your email address?", "text", 1),
                ("Briefly describe what happened.", "text", 2),
                ("When did this incident occur?", "text", 3)
            ]
            for text, q_type, order in questions:
                q = models.Question(
                    form_id=form.id,
                    text=text,
                    type=q_type,
                    order=order
                )
                db.add(q)
        else:
            form.qualification_rules = qualification_rules

        db.commit()
        print(f"Successfully provisioned/updated firm '{name}' ({slug}) with admin '{email}'.")
        print(f"Qualification rules generated and applied to the intake form.")
        
    except Exception as e:
        db.rollback()
        print(f"Error provisioning firm: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Provision a new firm account.")
    parser.add_argument("--name", required=True, help="Name of the law firm")
    parser.add_argument("--slug", required=True, help="URL-friendly slug for the firm")
    parser.add_argument("--email", required=True, help="Admin user email")
    parser.add_argument("--password", required=True, help="Admin user password")
    parser.add_argument("--branding", help="Path to branding-config.json")
    parser.add_argument("--criteria_text", help="Raw text of firm's qualification criteria")
    parser.add_argument("--criteria_url", help="URL of firm's website or practice areas page to extract criteria from")
    
    args = parser.parse_args()
    
    # Ensure tables exist
    models.Base.metadata.create_all(bind=engine)
    
    provision_firm(args.name, args.slug, args.email, args.password, args.branding, args.criteria_text, args.criteria_url)
