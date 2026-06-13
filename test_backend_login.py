import asyncio
import httpx
from fastapi.testclient import TestClient
from main import api_app # The inner app with routers

def test_login_logic():
    from database import SessionLocal
    from models import User
    from auth import verify_password
    
    db = SessionLocal()
    email = "attorney@lexiflow.tech"
    password = "TestPass123!"
    
    user = db.query(User).filter(User.email == email).first()
    print(f"User found: {user is not None}")
    if user:
        print(f"User email: {user.email}")
        print(f"User hash: {user.hashed_password}")
        match = verify_password(password, user.hashed_password)
        print(f"Password match: {match}")
    db.close()

if __name__ == "__main__":
    print("Testing direct logic:")
    test_login_logic()
    
    print("\nTesting via TestClient:")
    client = TestClient(api_app)
    response = client.post("/auth/login", data={"email": "attorney@lexiflow.tech", "password": "TestPass123!"})
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
