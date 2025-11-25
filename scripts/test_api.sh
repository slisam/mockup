#!/bin/bash
# Script de test manuel de l'API Transformations
# Usage: ./scripts/test_api.sh

set -e

API_URL="${API_URL:-http://localhost:8000}"
echo "🧪 Testing Transformations API at $API_URL"
echo "============================================"

# Couleurs pour l'output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
test_endpoint() {
    echo -e "\n${BLUE}Test: $1${NC}"
    echo "-------------------------------------------"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
}

# 1. Test de création de transformation
test_endpoint "POST /transformations - Créer une transformation"

# Créer un fichier Excel temporaire
echo "Creating temporary test files..."
echo "Test Excel Data" > /tmp/test.xlsx
echo "Test Word Data" > /tmp/test.docx

# Données JSON pour la transformation
TRANSFORMATION_DATA='{
  "carrier": "MSC",
  "trade_lane": "EU-US",
  "dates": [
    {
      "application_date": "2024-01-01",
      "validity_date": "2024-12-31"
    }
  ]
}'

# Envoi de la requête
RESPONSE=$(curl -s -X POST "$API_URL/transformations" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "excel_file=@/tmp/test.xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
  -F "word_file=@/tmp/test.docx;type=application/vnd.openxmlformats-officedocument.wordprocessingml.document" \
  -F "data=$TRANSFORMATION_DATA")

echo "$RESPONSE" | jq '.'

# Extraire l'ID de la transformation créée
TRANSFORMATION_ID=$(echo "$RESPONSE" | jq -r '.items[0].id')

if [ "$TRANSFORMATION_ID" != "null" ] && [ -n "$TRANSFORMATION_ID" ]; then
    success "Transformation créée avec ID: $TRANSFORMATION_ID"
else
    error "Échec de création de transformation"
    exit 1
fi

# 2. Test de listing
test_endpoint "GET /transformations - Lister les transformations"

LIST_RESPONSE=$(curl -s "$API_URL/transformations?limit=10")
echo "$LIST_RESPONSE" | jq '.'

ITEM_COUNT=$(echo "$LIST_RESPONSE" | jq '.items | length')
success "Nombre de transformations: $ITEM_COUNT"

# 3. Test de listing avec filtres
test_endpoint "GET /transformations - Filtrage par carrier"

FILTER_RESPONSE=$(curl -s "$API_URL/transformations?carrier=MSC&limit=5")
echo "$FILTER_RESPONSE" | jq '.'
success "Filtrage par carrier fonctionne"

# 4. Test de récupération des détails de statut
test_endpoint "GET /transformations/{id}/status-details-in-progress"

if [ -n "$TRANSFORMATION_ID" ]; then
    STATUS_RESPONSE=$(curl -s "$API_URL/transformations/$TRANSFORMATION_ID/status-details-in-progress")
    echo "$STATUS_RESPONSE" | jq '.'
    success "Détails de statut récupérés"
fi

# 5. Test d'erreur 404
test_endpoint "GET /transformations/{invalid_id}/status-details-in-progress - Test 404"

ERROR_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    "$API_URL/transformations/invalid-uuid-123/status-details-in-progress")

HTTP_CODE=$(echo "$ERROR_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)

if [ "$HTTP_CODE" = "404" ]; then
    success "404 Not Found retourné correctement"
else
    error "Code HTTP attendu: 404, reçu: $HTTP_CODE"
fi

# Nettoyage
rm -f /tmp/test.xlsx /tmp/test.docx

echo -e "\n${GREEN}============================================"
echo "✓ Tous les tests sont passés!"
echo "============================================${NC}"
