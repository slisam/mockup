#!/usr/bin/env python3
"""Initialize the database tables.

Run this from the project root: python scripts/init_db.py
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Force local mode to avoid GCS dependency
os.environ['MODE'] = 'local'

from app.core.db.session import engine, Base
from app.models.transformations import Transformation


def init_db() -> None:
    """Create all tables defined in SQLAlchemy models."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")
    print(f"Tables: {', '.join(Base.metadata.tables.keys())}")


if __name__ == "__main__":
    init_db()
