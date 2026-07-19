"""
LexiFlow Database Configuration

Supports multiple database backends:
1. Turso/libsql (production) — set DATABASE_URL to a libsql:// URL
2. SQLite (local development) — default when no DATABASE_URL is set
3. Vercel /tmp SQLite — automatic fallback on Vercel when no DATABASE_URL is set

Set DATABASE_URL to a Turso connection string for production:
  libsql://<database-name>.turso.io?authToken=<token>

For local development, leave DATABASE_URL unset to use local SQLite.
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Determine the database URL
db_url = os.getenv("DATABASE_URL")

if not db_url:
    # Check for Turso environment variables (set by the platform integration)
    turso_url = os.getenv("turso_database_url") or os.getenv("TURSO_DATABASE_URL")
    turso_token = os.getenv("turso_auth_token") or os.getenv("TURSO_AUTH_TOKEN")
    if turso_url and turso_token:
        # Construct libsql URL with auth token
        db_url = f"{turso_url}?authToken={turso_token}"
        logger.info("Using Turso edge database from environment variables")
    # Check if we are in a Vercel environment
    elif os.getenv("VERCEL") or os.getenv("NOW_REGION"):
        db_url = "sqlite:////tmp/lexiflow.db"
        # Seed the /tmp database from the repository file if it doesn't exist
        import shutil
        if not os.path.exists("/tmp/lexiflow.db"):
            repo_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lexiflow.db")
            if os.path.exists(repo_db):
                try:
                    shutil.copy2(repo_db, "/tmp/lexiflow.db")
                    logger.info("Seeded /tmp/lexiflow.db from repository")
                except Exception as e:
                    logger.warning(f"Failed to seed /tmp/lexiflow.db: {e}")
    else:
        # Use absolute path to avoid directory confusion
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "lexiflow.db")
        db_url = f"sqlite:///{db_path}"

SQLALCHEMY_DATABASE_URL = db_url
logger.info(f"Database URL scheme: {db_url.split('://')[0] if '://' in db_url else 'unknown'}")

# Configure engine based on database type
connect_args = {}
engine_kwargs = {}

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLite needs check_same_thread=False for FastAPI async usage
    connect_args = {"check_same_thread": False}
elif SQLALCHEMY_DATABASE_URL.startswith("libsql"):
    # Turso/libsql — use the libsql dialect from sqlalchemy-libsql
    # The libsql dialect handles its own connection pooling
    # No special connect_args needed for libsql
    pass

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database Session Error: {e}")
        raise
    finally:
        db.close()


def check_connection() -> bool:
    """Verify the database connection is working."""
    try:
        db = SessionLocal()
        db.execute(db.bind.dialect.statement_compiler(db.bind.dialect, None).__class__.__name__)
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
