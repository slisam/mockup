# 🧪 Guide Complet de Test

Documentation complète sur les tests de l'API transformations avec SQLAlchemy.

[... Le contenu reste identique jusqu'à la section débogage ...]

## 🔍 Vérifier l'état de la base de données

### Avec Python et SQLAlchemy

```bash
# Afficher la structure
python scripts/check_db.py

# Compter les transformations
MODE=local python3 -c "
from app.core.db.session import SessionLocal
from app.models.transformations import Transformation
db = SessionLocal()
print(f'Total: {db.query(Transformation).count()} transformations')
db.close()
"

# Voir les dernières transformations
MODE=local python3 -c "
from app.core.db.session import SessionLocal
from app.models.transformations import Transformation
db = SessionLocal()
transformations = db.query(Transformation).order_by(Transformation.created_at.desc()).limit(5).all()
for t in transformations:
    print(f'{t.id[:8]}... | {t.carrier} | {t.status}')
db.close()
"
```

### Inspecter la base de données

```bash
# Inspecter avec SQLAlchemy
MODE=local python3 <<EOF
from sqlalchemy import inspect
from app.core.db.session import engine, SessionLocal
from app.models.transformations import Transformation

# Structure
inspector = inspect(engine)
print("Tables:", inspector.get_table_names())
for table in inspector.get_table_names():
    print(f"\nTable: {table}")
    for col in inspector.get_columns(table):
        print(f"  {col['name']}: {col['type']}")

# Données
db = SessionLocal()
transformations = db.query(Transformation).limit(5).all()
print(f"\nPremières transformations:")
for t in transformations:
    print(f"{t.id[:8]}... | {t.carrier} | {t.trade_lane} | {t.status}")
db.close()
EOF
```
