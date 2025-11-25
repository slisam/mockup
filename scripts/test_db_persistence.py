#!/usr/bin/env python3
"""
Script de test pour vérifier l'enregistrement des transformations dans la BD.
Usage: python scripts/test_db_persistence.py
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Force local mode
os.environ['MODE'] = 'local'

from sqlalchemy import text
from app.core.db.session import engine, SessionLocal
from app.models.transformations import Transformation

def test_database_persistence():
    """Test that transformations are persisted in the database."""

    print("🧪 Test de persistance de la base de données")
    print("=" * 80)

    db = SessionLocal()

    try:
        # 1. Compter les transformations existantes
        initial_count = db.query(Transformation).count()
        print(f"\n1️⃣  Nombre de transformations au début: {initial_count}")

        # 2. Créer une transformation de test
        print("\n2️⃣  Création d'une transformation de test...")
        from uuid import uuid4
        from datetime import datetime, timezone

        test_id = str(uuid4())
        test_transformation = Transformation(
            id=test_id,
            created_at=datetime.now(timezone.utc),
            status="SENT_TO_DMP",
            carrier="TEST_CARRIER",
            trade_lane="TEST-LANE",
            xlsx_name="test.xlsx",
            docx_name="test.docx",
            progress=0,
            message="Test de persistance"
        )

        test_transformation.set_transformation_data({
            "carrier": "TEST_CARRIER",
            "trade_lane": "TEST-LANE",
            "dates": [{"application_date": "2024-01-01", "validity_date": "2024-12-31"}]
        })

        test_transformation.set_status_details({
            "UPLOAD_COMPLETE": True,
            "PROCESSING": False,
            "REVIEW": False,
            "READY_TO_PUBLISH": False
        })

        db.add(test_transformation)
        db.commit()
        print(f"   ✅ Transformation créée avec ID: {test_id}")

        # 3. Fermer la session et en créer une nouvelle
        db.close()
        db = SessionLocal()
        print("\n3️⃣  Nouvelle session créée (pour vérifier la persistance)")

        # 4. Récupérer depuis la BD
        print(f"\n4️⃣  Récupération de la transformation depuis la BD...")
        retrieved = db.query(Transformation).filter(Transformation.id == test_id).first()

        if retrieved:
            print(f"   ✅ Transformation retrouvée !")
            print(f"   - ID: {retrieved.id}")
            print(f"   - Carrier: {retrieved.carrier}")
            print(f"   - Trade Lane: {retrieved.trade_lane}")
            print(f"   - Status: {retrieved.status}")
            print(f"   - Created at: {retrieved.created_at}")
            print(f"   - Files: {retrieved.xlsx_name}, {retrieved.docx_name}")

            # Vérifier les données JSON
            transformation_data = retrieved.get_transformation_data()
            if transformation_data:
                print(f"   - Transformation data: {transformation_data}")

            status_details = retrieved.get_status_details()
            print(f"   - Status details: {status_details}")
        else:
            print(f"   ❌ Transformation NON retrouvée (problème de persistance !)")
            return False

        # 5. Vérifier le nombre total
        final_count = db.query(Transformation).count()
        print(f"\n5️⃣  Nombre de transformations à la fin: {final_count}")
        print(f"   Différence: +{final_count - initial_count}")

        # 6. Lister toutes les transformations
        print(f"\n6️⃣  Liste de toutes les transformations:")
        all_transformations = db.query(Transformation).order_by(Transformation.created_at.desc()).limit(10).all()
        for i, t in enumerate(all_transformations, 1):
            print(f"   {i}. ID: {t.id[:8]}... | Carrier: {t.carrier:<15} | Trade Lane: {t.trade_lane:<10} | Status: {t.status}")

        # 7. Requête SQL directe pour vérifier
        print(f"\n7️⃣  Vérification avec requête SQL directe:")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as count FROM transformations"))
            count = result.fetchone()[0]
            print(f"   Nombre de lignes dans la table: {count}")

            result = conn.execute(text("SELECT id, carrier, trade_lane, status FROM transformations ORDER BY created_at DESC LIMIT 5"))
            rows = result.fetchall()
            for row in rows:
                print(f"   - {row[0][:8]}... | {row[1]} | {row[2]} | {row[3]}")

        print("\n" + "=" * 80)
        print("✅ TEST RÉUSSI : Les transformations sont bien persistées dans la BD !")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = test_database_persistence()
    sys.exit(0 if success else 1)
