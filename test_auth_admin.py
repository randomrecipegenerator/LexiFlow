import bcrypt

# The hash from the database for admin@lexiflow.tech
hashed = b"$2b$12$tjWJ1E1NOe/eOW/VvH0lRudxe8lFB7Wip1IVfX8v/9vmQ2kWlgAAW"
password = b"TestPass123!"

try:
    match = bcrypt.checkpw(password, hashed)
    print(f"Match: {match}")
except Exception as e:
    print(f"Error: {e}")
