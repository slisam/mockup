from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
from app.core import config
from app.services.gcs_db import download_sqlite_from_gcs

# -----------------------------------
# Resolve DB path (local or cloud)
# -----------------------------------

if config.MODE == "local":
    # Preserve old logic for LOCAL development
    DB_MODULE_DIR = Path(__file__).resolve().parent
    APP_DIR = DB_MODULE_DIR.parent
    PROJECT_ROOT = APP_DIR.parent
    PARENT_DIR = PROJECT_ROOT.parent

    # Example: /.../ratecard-dump/ratecard.sqlite
    DUMP_DIR = PARENT_DIR / "ratecard-dump"
    DUMP_DIR.mkdir(parents=True, exist_ok=True)

    DB_FILE = DUMP_DIR / "ratecard.sqlite"
    DB_FILE_PATH = str(DB_FILE)

else:
    # Cloud mode → download SQLite file from GCS
    DB_FILE_PATH = download_sqlite_from_gcs()

# -----------------------------------
# SQLAlchemy Engine & Session
# -----------------------------------

# Use SQLite for now, but can switch to PostgreSQL easily by changing DATABASE_URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    """Provide a SQLAlchemy session for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
