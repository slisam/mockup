#!/usr/bin/env python3
"""Check database structure and display table schemas.

Run this from the project root: python scripts/check_db.py
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Force local mode to avoid GCS dependency
os.environ['MODE'] = 'local'

from sqlalchemy import inspect
from app.core.db.session import engine


def check_db() -> None:
    """Display database structure information."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"Tables in database: {', '.join(tables)}")
    print()

    for table in tables:
        print(f"\nTable: {table}")
        print("-" * 80)
        columns = inspector.get_columns(table)
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"  {col['name']:<30} {str(col['type']):<20} {nullable}")


if __name__ == "__main__":
    check_db()
