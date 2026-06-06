import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use environment variable for DB URL, default to local SQLite for development
# On Vercel, the filesystem is read-only, so we use /tmp for SQLite if no DATABASE_URL is provided.
db_url = os.getenv("DATABASE_URL")
if not db_url:
    # Check if we are in a Vercel environment
    if os.getenv("VERCEL") or os.getenv("NOW_REGION"):
        db_url = "sqlite:////tmp/lexiflow.db"
    else:
        db_url = "sqlite:///./lexiflow.db"

SQLALCHEMY_DATABASE_URL = db_url

# Standard SQLAlchemy setup
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Database Session Error: {e}")
        raise
    finally:
        db.close()
