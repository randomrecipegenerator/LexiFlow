import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        print(f"Error: {e}")
        return False

# Attorney from DB
attorney_hash = "$2b$12$08wqy9TnUEFkbBY12HZEPOoogNfiPDUNVV6vYCG2yqAPc3J6B414O"
# Admin from DB
admin_hash = "$2b$12$Uf6rM2P1wB4u8y8O6H3zHe0Z6M2r4j5O6P7Q8R9S0T1U2V3W4X5Y6" # Wait, I updated it earlier but let's check current DB

import sqlite3
conn = sqlite3.connect("lexiflow.db")
cursor = conn.cursor()
cursor.execute("SELECT email, hashed_password FROM users")
users = cursor.fetchall()
conn.close()

password = "TestPass123!"

for email, h in users:
    match = verify_password(password, h)
    print(f"User: {email}")
    print(f"Hash: {h}")
    print(f"Match: {match}")
    print("-" * 20)
