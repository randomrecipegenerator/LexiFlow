import bcrypt

# The hash from the database for attorney@lexiflow.tech
hashed = b"$2b$12$08wqy9TnUEFkbBY12HZEPOoogNfiPDUNVV6vYCG2yqAPc3J6B414O"
password = b"TestPass123!"

try:
    match = bcrypt.checkpw(password, hashed)
    print(f"Match: {match}")
except Exception as e:
    print(f"Error: {e}")
