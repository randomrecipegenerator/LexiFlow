import bcrypt
import sqlite3

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

password = "TestPass123!"
new_hash = hash_password(password)

conn = sqlite3.connect("lexiflow.db")
cursor = conn.cursor()
cursor.execute("UPDATE users SET hashed_password = ?", (new_hash,))
conn.commit()
print(f"Updated {cursor.rowcount} users to use TestPass123! with hash: {new_hash}")
conn.close()
