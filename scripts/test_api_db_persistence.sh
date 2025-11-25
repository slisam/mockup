#!/bin/bash
# Test complet : API → Base de données
# Usage: ./scripts/test_api_db_persistence.sh

set -e

API_URL="${API_URL:-http://localhost:8000}"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🧪 Test complet : Création via API → Vérification dans la BD${NC}"
echo "=========================================================================="

# 1. Vérifier que le serveur est démarré
echo ""
echo -e "${YELLOW}1️⃣  Vérification du serveur...${NC}"
if ! curl -s "$API_URL/" > /dev/null 2>&1; then
    echo -e "❌ Serveur non accessible. Démarrez-le avec:"
    echo -e "   MODE=local uvicorn app.main:app --host 0.0.0.0 --port 8000"
    exit 1
fi
echo -e "${GREEN}✓ Serveur accessible${NC}"

# 2. Compter les transformations avant
echo ""
echo -e "${YELLOW}2️⃣  Nombre de transformations avant:${NC}"
BEFORE_COUNT=$(curl -s "$API_URL/transformations?limit=100" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['items']))")
echo -e "   ${BEFORE_COUNT} transformation(s)"

# 3. Créer des fichiers de test
echo ""
echo -e "${YELLOW}3️⃣  Création de fichiers de test...${NC}"
echo "Test Excel Content" > /tmp/test_api.xlsx
echo "Test Word Content" > /tmp/test_api.docx
echo -e "${GREEN}✓ Fichiers créés${NC}"

# 4. Créer une transformation via l'API
echo ""
echo -e "${YELLOW}4️⃣  Création d'une transformation via POST /transformations...${NC}"

TRANSFORMATION_DATA='{
  "carrier": "API_TEST_MSC",
  "trade_lane": "EU-ASIA",
  "dates": [
    {
      "application_date": "2024-01-01",
      "validity_date": "2024-12-31"
    }
  ]
}'

RESPONSE=$(curl -s -X POST "$API_URL/transformations" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "excel_file=@/tmp/test_api.xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
  -F "word_file=@/tmp/test_api.docx;type=application/vnd.openxmlformats-officedocument.wordprocessingml.document" \
  -F "data=$TRANSFORMATION_DATA")

echo "$RESPONSE" | python3 -m json.tool

# Extraire l'ID
TRANSFORMATION_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['items'][0]['id'])")

if [ -n "$TRANSFORMATION_ID" ]; then
    echo -e "${GREEN}✓ Transformation créée avec ID: $TRANSFORMATION_ID${NC}"
else
    echo -e "❌ Échec de création"
    exit 1
fi

# 5. Attendre un peu (pour être sûr)
sleep 1

# 6. Récupérer via GET /transformations
echo ""
echo -e "${YELLOW}5️⃣  Récupération via GET /transformations...${NC}"
LIST_RESPONSE=$(curl -s "$API_URL/transformations?limit=100")
echo "$LIST_RESPONSE" | python3 -m json.tool | head -30

# Vérifier que notre transformation est dans la liste
FOUND=$(echo "$LIST_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
found = any(item['id'] == '$TRANSFORMATION_ID' for item in data['items'])
print('yes' if found else 'no')
")

if [ "$FOUND" = "yes" ]; then
    echo -e "${GREEN}✓ Transformation retrouvée dans la liste${NC}"
else
    echo -e "❌ Transformation NON retrouvée"
    exit 1
fi

# 7. Récupérer les détails de statut
echo ""
echo -e "${YELLOW}6️⃣  Récupération des détails de statut...${NC}"
STATUS_RESPONSE=$(curl -s "$API_URL/transformations/$TRANSFORMATION_ID/status-details-in-progress")
echo "$STATUS_RESPONSE" | python3 -m json.tool

# 8. Compter après
echo ""
echo -e "${YELLOW}7️⃣  Nombre de transformations après:${NC}"
AFTER_COUNT=$(curl -s "$API_URL/transformations?limit=100" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['items']))")
echo -e "   ${AFTER_COUNT} transformation(s)"
echo -e "   Différence: +$((AFTER_COUNT - BEFORE_COUNT))"

# 9. Vérification directe dans la BD
echo ""
echo -e "${YELLOW}8️⃣  Vérification directe dans la base de données SQLite:${NC}"
MODE=local python3 <<EOF
import os
os.environ['MODE'] = 'local'
from app.core.db.session import SessionLocal
from app.models.transformations import Transformation

db = SessionLocal()
try:
    # Récupérer la transformation par ID
    t = db.query(Transformation).filter(Transformation.id == "$TRANSFORMATION_ID").first()
    if t:
        print(f"   ✓ Transformation trouvée dans la BD:")
        print(f"     - ID: {t.id}")
        print(f"     - Carrier: {t.carrier}")
        print(f"     - Trade Lane: {t.trade_lane}")
        print(f"     - Status: {t.status}")
        print(f"     - Created: {t.created_at}")
        print(f"     - Files: {t.xlsx_name}, {t.docx_name}")

        # Données JSON
        data = t.get_transformation_data()
        if data:
            print(f"     - Data carrier: {data.get('carrier')}")
            print(f"     - Data trade_lane: {data.get('trade_lane')}")

        status = t.get_status_details()
        print(f"     - Upload complete: {status.get('UPLOAD_COMPLETE')}")
    else:
        print("   ✗ Transformation NON trouvée dans la BD")
        exit(1)
finally:
    db.close()
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================================================="
    echo -e "${GREEN}✅ TEST RÉUSSI : La persistance fonctionne parfaitement !${NC}"
    echo ""
    echo "Workflow complet vérifié :"
    echo "  1. ✓ Création via API POST /transformations"
    echo "  2. ✓ Enregistrement dans la base de données SQLite"
    echo "  3. ✓ Récupération via API GET /transformations"
    echo "  4. ✓ Vérification directe dans la BD"
    echo "=========================================================================="
else
    echo ""
    echo "❌ TEST ÉCHOUÉ : Problème de persistance"
    exit 1
fi

# Nettoyage
rm -f /tmp/test_api.xlsx /tmp/test_api.docx
