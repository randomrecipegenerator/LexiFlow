import sys
import os

# Add the parent directory to sys.path to import the backend module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import models
from database import engine

def init_db():
    print("Initializing database...")
    models.Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
