"""
Script to initialize the transformations table in the database.
This creates the necessary schema for storing transformations.
"""
from app.core.db.session import engine, Base
from app.models.transformations import Transformation


def init_transformations_db():
    """Create all tables defined in SQLAlchemy models"""
    print("Creating transformations table...")
    Base.metadata.create_all(bind=engine)
    print("Transformations table created successfully!")


if __name__ == "__main__":
    init_transformations_db()
