import bcrypt
import sqlite3

# New password
password = b"TestPass123!"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password, salt).decode('utf-8')

# Update database
db_path = "/home/team/shared/LexiFlow-Final/lexiflow.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("UPDATE users SET hashed_password = ? WHERE email = ?", (hashed, "admin@lexiflow.tech"))
conn.commit()

print(f"Updated admin@lexiflow.tech password to TestPass123!. New hash: {hashed}")

# Also update the local admin account just in case they are using that
cursor.execute("UPDATE users SET hashed_password = ? WHERE email = ?", (hashed, "admin@lexiflow-tech.local"))
conn.commit()
print("Updated admin@lexiflow-tech.local password to TestPass123!.")

conn.close()
