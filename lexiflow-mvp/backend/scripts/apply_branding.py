import os
import sys
import json
from sqlalchemy.orm import Session

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend import models
from backend.database import SessionLocal

def apply_branding(slug, config_path):
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        return

    with open(config_path, 'r') as f:
        config = json.load(f)

    db = SessionLocal()
    try:
        firm = db.query(models.Firm).filter(models.Firm.slug == slug).first()
        if not firm:
            print(f"Firm with slug '{slug}' not found.")
            return

        branding = config.get('branding', {})
        
        # Update logo
        firm.branding_logo = branding.get('logo')
        
        # Update colors (store as JSON string)
        colors = branding.get('colors', {})
        firm.branding_colors = json.dumps(colors)
        
        # Update name if provided in config
        if 'firm_name' in config:
            firm.name = config['firm_name']

        db.commit()
        print(f"Successfully applied branding to '{firm.name}' ({slug}).")
        
    except Exception as e:
        db.rollback()
        print(f"Error applying branding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Clifford Law
    apply_branding("clifford-law", "/home/team/shared/branding/clifford-law-assets/branding-config.json")
    
    # Smith LaCien
    apply_branding("smith-lacien", "/home/team/shared/branding/smith-lacien-assets/branding-config.json")
