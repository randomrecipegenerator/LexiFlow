import models
from database import SessionLocal, engine
from auth import hash_password

def init_db():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Create a default firm if not exists
    firm = db.query(models.Firm).filter(models.Firm.slug == "lexiflow-tech").first()
    if not firm:
        firm = models.Firm(
            name="LexiFlow Technologies Inc",
            slug="lexiflow-tech",
            desktop_api_key="lf_desktop_69c23418a598d2c60c359f0dadb24326565618661cf46c897e2f06e4ed9e5c6f",
            api_config_json='{"desktop_api_key": "lf_desktop_69c23418a598d2c60c359f0dadb24326565618661cf46c897e2f06e4ed9e5c6f"}'
        )
        db.add(firm)
        db.commit()
        db.refresh(firm)
        print(f"Firm created: {firm.name}")

    # Create users for all firms
    firms = db.query(models.Firm).all()
    for f in firms:
        user_email = f"admin@{f.slug}.local"
        user = db.query(models.User).filter(models.User.email == user_email).first()
        if not user:
            user = models.User(
                email=user_email,
                hashed_password=hash_password("admin123"),
                full_name=f"{f.name} Admin",
                firm_id=f.id,
                role="admin",
                is_active=1
            )
            db.add(user)
            db.commit()
            print(f"User created: {user.email}")
        
    db.close()

if __name__ == "__main__":
    init_db()
