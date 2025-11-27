# Guide de Test Swagger - Endpoints Transformations

## Lancer l'API
```bash
MODE=local uvicorn app.main:app --reload --port 8000
```

Puis ouvrir: **http://localhost:8000/docs**

---

## Exemples de Données pour POST /transformations

### Exemple 1: MAERSK / US-ASIA
```json
{
  "carrier": "MAERSK",
  "trade_lane": "US-ASIA",
  "dates": [
    {
      "application_date": "2024-01-01",
      "validity_date": "2024-12-31"
    }
  ]
}
```

### Exemple 2: HAPAG-LLOYD / EUR-MENA
```json
{
  "carrier": "HAPAG-LLOYD",
  "trade_lane": "EUR-MENA",
  "dates": [
    {
      "application_date": "2024-02-01",
      "validity_date": "2024-11-30"
    }
  ]
}
```

### Exemple 3: CMA-CGM / ASIA-AFR
```json
{
  "carrier": "CMA-CGM",
  "trade_lane": "ASIA-AFR",
  "dates": [
    {
      "application_date": "2024-03-15",
      "validity_date": "2024-09-15"
    }
  ]
}
```

---

## Format ID Généré
Les IDs sont générés automatiquement au format:
```
{carrier}_{trade_lane}_{timestamp}
```

Exemples:
- `MAERSK_US-ASIA_20251127120000123456`
- `HAPAG-LLOYD_EUR-MENA_20251127120100234567`
- `CMA-CGM_ASIA-AFR_20251127120200345678`

---

## État Actuel de la DB
- **Transformations**: 3
- **Trade Lanes**: ["ASIA-EUR", "EU-US", "TEST-LANE"]

---

## Endpoints Disponibles

### 1. GET /trade-lanes
Retourne la liste des trade lanes uniques

### 2. GET /transformations
Liste toutes les transformations avec filtres optionnels:
- `carrier`: Filtrer par carrier
- `trade_lane`: Filtrer par trade lane
- `status`: Filtrer par statut
- `limit`: Nombre de résultats (default: 20)

### 3. POST /transformations
Créer une nouvelle transformation
- Fichiers: excel_file (.xlsx), word_file (.docx)
- Data: JSON avec carrier, trade_lane, dates

### 4. GET /transformations/{id}/status-details-in-progress
Obtenir le statut détaillé d'une transformation
