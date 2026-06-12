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
        # Seed the /tmp database from the repository file if it doesn't exist
        import shutil
        if not os.path.exists("/tmp/lexiflow.db"):
            repo_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lexiflow.db")
            if os.path.exists(repo_db):
                try:
                    shutil.copy2(repo_db, "/tmp/lexiflow.db")
                    print("Seeded /tmp/lexiflow.db from repository")
                except Exception as e:
                    print(f"Failed to seed /tmp/lexiflow.db: {e}")
    else:
        # Use absolute path to avoid directory confusion
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "lexiflow.db")
        db_url = f"sqlite:///{db_path}"

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
