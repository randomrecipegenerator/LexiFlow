
import bcrypt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import User, Base
import os

# Database setup
db_path = "/home/team/shared/LexiFlow-Final/lexiflow.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def test_login(email, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(func.lower(User.email) == func.lower(email)).first()
        if not user:
            print(f"User {email} not found")
            return False
        
        print(f"Found user: {user.email}")
        print(f"Hashed password in DB: {user.hashed_password}")
        
        is_valid = verify_password(password, user.hashed_password)
        print(f"Password valid: {is_valid}")
        return is_valid
    finally:
        db.close()

if __name__ == "__main__":
    print("Testing admin@lexiflow.tech / TestPass123!")
    test_login("admin@lexiflow.tech", "TestPass123!")
    
    print("\nTesting attorney@lexiflow.tech / TestPass123!")
    test_login("attorney@lexiflow.tech", "TestPass123!")

    print("\nTesting with incorrect password")
    test_login("admin@lexiflow.tech", "wrongpassword")
