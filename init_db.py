"""
Simple script to initialize the database tables.
Run this from the project root: python init_db.py
"""
import os

# Force local mode to avoid GCS dependency
os.environ['MODE'] = 'local'

from app.core.db.session import engine, Base
from app.models.transformations import Transformation

def init_db():
    """Create all tables defined in SQLAlchemy models"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    print(f"Tables: {Base.metadata.tables.keys()}")

if __name__ == "__main__":
    init_db()
