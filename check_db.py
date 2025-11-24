"""
Check database structure
"""
import os
os.environ['MODE'] = 'local'

from sqlalchemy import inspect
from app.core.db.session import engine

inspector = inspect(engine)
tables = inspector.get_table_names()

print(f"Tables in database: {tables}")
print()

for table in tables:
    print(f"\nTable: {table}")
    print("-" * 50)
    columns = inspector.get_columns(table)
    for col in columns:
        print(f"  {col['name']:<30} {str(col['type']):<20} nullable={col['nullable']}")
