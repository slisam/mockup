from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
from app.core import config
import os

MODE = os.getenv("MODE", "local")

if MODE == "local":
    DB_MODULE_DIR = Path(__file__).resolve().parent
    APP_DIR = DB_MODULE_DIR.parent
    PROJECT_ROOT = APP_DIR.parent
    PARENT_DIR = PROJECT_ROOT.parent
    DUMP_DIR = PARENT_DIR / "ratecard-dump"
    DUMP_DIR.mkdir(parents=True, exist_ok=True)
    DB_FILE = DUMP_DIR / "ratecard.sqlite"
    DB_FILE_PATH = str(DB_FILE)
else:
    from app.services.gcs_db import download_sqlite_from_gcs
    DB_FILE_PATH = download_sqlite_from_gcs()

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
