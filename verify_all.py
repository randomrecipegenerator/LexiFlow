import bcrypt
import sqlite3

password = b"TestPass123!"
db_path = "lexiflow.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
users = cursor.execute("SELECT email, hashed_password FROM users").fetchall()
conn.close()

for email, hashed in users:
    try:
        match = bcrypt.checkpw(password, hashed.encode('utf-8'))
        print(f"User: {email}, Match: {match}")
    except Exception as e:
        print(f"User: {email}, Error: {e}")
