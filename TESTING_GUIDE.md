# 🧪 Guide Complet de Test

Ce guide explique comment tester l'application de transformations SQLAlchemy.

## 📋 Table des matières

1. [Installation](#installation)
2. [Initialisation](#initialisation)
3. [Tests manuels avec l'interface Swagger](#tests-swagger)
4. [Tests avec curl](#tests-curl)
5. [Tests automatisés avec pytest](#tests-pytest)
6. [Tests de performance](#tests-performance)

---

## 🔧 Installation

### 1. Installer les dépendances

```bash
# Dépendances de base
pip install -r requirements.txt

# Dépendances de développement (tests)
pip install -r requirements-dev.txt
```

### 2. Initialiser la base de données

```bash
python scripts/init_db.py
```

**Résultat attendu :**
```
Creating database tables...
✓ Database tables created successfully!
Tables: transformations
```

---

## 🚀 Démarrer l'application

### Méthode 1 : Script de développement

```bash
python scripts/run_dev.py
```

### Méthode 2 : Uvicorn direct

```bash
MODE=local uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Résultat attendu :**
```
🚀 Starting FastAPI server in development mode...
📍 Server will be available at: http://localhost:8000
📚 API documentation at: http://localhost:8000/docs
```

---

## 📖 Tests manuels avec Swagger UI

### 1. Accéder à la documentation interactive

Ouvrez votre navigateur : **http://localhost:8000/docs**

### 2. Créer une transformation

1. Cliquez sur **POST /transformations**
2. Cliquez sur **Try it out**
3. Uploadez les fichiers :
   - `excel_file`: fichier .xlsx
   - `word_file`: fichier .docx
4. Remplissez le champ `data` :

```json
{
  "carrier": "MSC",
  "trade_lane": "EU-US",
  "dates": [
    {
      "application_date": "2024-01-01",
      "validity_date": "2024-12-31"
    }
  ]
}
```

5. Cliquez sur **Execute**

**Résultat attendu (201 Created) :**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2024-01-15T10:30:00.000Z",
      "status": "SENT_TO_DMP",
      "carrier": "MSC",
      "trade_lane": "EU-US",
      "file_names": {
        "xlsx_name": "test.xlsx",
        "docx_name": "test.docx"
      }
    }
  ],
  "next_cursor": null
}
```

### 3. Lister les transformations

1. Cliquez sur **GET /transformations**
2. Cliquez sur **Try it out**
3. Paramètres optionnels :
   - `limit`: 20
   - `carrier`: MSC
   - `status`: SENT_TO_DMP
4. Cliquez sur **Execute**

### 4. Obtenir les détails de statut

1. Copiez l'ID d'une transformation
2. Cliquez sur **GET /transformations/{id}/status-details-in-progress**
3. Collez l'ID
4. Cliquez sur **Execute**

---

## 💻 Tests avec curl

### Script automatique

```bash
# Rendre le script exécutable
chmod +x scripts/test_api.sh

# Lancer les tests
./scripts/test_api.sh
```

### Commandes manuelles

#### 1. Créer une transformation

```bash
# Créer des fichiers temporaires
echo "Excel data" > /tmp/test.xlsx
echo "Word data" > /tmp/test.docx

# Envoi de la requête
curl -X POST "http://localhost:8000/transformations" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "excel_file=@/tmp/test.xlsx" \
  -F "word_file=@/tmp/test.docx" \
  -F 'data={"carrier":"MSC","trade_lane":"EU-US","dates":[{"application_date":"2024-01-01","validity_date":"2024-12-31"}]}'
```

#### 2. Lister toutes les transformations

```bash
curl "http://localhost:8000/transformations?limit=10" | jq
```

#### 3. Filtrer par carrier

```bash
curl "http://localhost:8000/transformations?carrier=MSC&limit=5" | jq
```

#### 4. Filtrer par date

```bash
curl "http://localhost:8000/transformations?date.start=2024-01-01&date.end=2024-12-31" | jq
```

#### 5. Obtenir les détails de statut

```bash
# Remplacer {ID} par un vrai ID
curl "http://localhost:8000/transformations/{ID}/status-details-in-progress" | jq
```

#### 6. Test d'erreur 404

```bash
curl -i "http://localhost:8000/transformations/invalid-id/status-details-in-progress"
```

**Résultat attendu :**
```
HTTP/1.1 404 Not Found
{
  "detail": "Transformation invalid-id not found"
}
```

---

## 🧪 Tests automatisés avec pytest

### Lancer tous les tests

```bash
pytest
```

**Résultat attendu :**
```
================================ test session starts =================================
collected 20 items

tests/test_models.py ........                                              [ 40%]
tests/test_services.py ......                                              [ 70%]
tests/test_api.py ......                                                   [100%]

================================ 20 passed in 2.34s ==================================
```

### Tests avec couverture de code

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

**Résultat attendu :**
```
---------- coverage: platform linux, python 3.11.0 -----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
app/models/transformations.py             45      0   100%
app/services/transformations.py           78      2    97%
app/api/routes/transformations.py         32      1    97%
-----------------------------------------------------------
TOTAL                                     155      3    98%
```

### Lancer des tests spécifiques

```bash
# Tests de modèles uniquement
pytest tests/test_models.py

# Tests de services uniquement
pytest tests/test_services.py

# Tests d'API uniquement
pytest tests/test_api.py

# Un test spécifique
pytest tests/test_models.py::TestTransformationModel::test_create_transformation

# Tests avec pattern
pytest -k "create"
```

### Tests en mode verbose

```bash
pytest -v
```

### Tests avec affichage des prints

```bash
pytest -s
```

---

## 📊 Structure des tests

### Tests unitaires (`test_models.py`)

Testent les modèles SQLAlchemy en isolation :
- Création d'instances
- Conversion to_dict()
- Stockage/récupération JSON
- Gestion d'erreurs JSON corrompu
- Valeurs par défaut

### Tests de services (`test_services.py`)

Testent la logique métier :
- Validation des entrées
- Création de transformations
- Filtrage et pagination
- Gestion d'erreurs (404, 500)
- Transactions et rollback

### Tests d'intégration (`test_api.py`)

Testent l'API complète :
- Endpoints HTTP
- Validation des fichiers
- Codes de statut HTTP
- Réponses JSON
- Cas d'erreur

---

## 🎯 Exemples de tests

### Tester la création

```python
def test_create_transformation(client):
    response = client.post("/transformations", ...)
    assert response.status_code == 201
    assert response.json()["items"][0]["carrier"] == "MSC"
```

### Tester le filtrage

```python
def test_filter_by_carrier(client):
    # Créer 2 transformations MSC, 1 CMA
    ...

    response = client.get("/transformations?carrier=MSC")
    assert len(response.json()["items"]) == 2
```

### Tester les erreurs

```python
def test_404_not_found(client):
    response = client.get("/transformations/invalid-id/status-details-in-progress")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
```

---

## 🔍 Vérifier l'état de la base de données

```bash
# Afficher la structure
python scripts/check_db.py

# Compter les transformations
sqlite3 ../ratecard-dump/ratecard.sqlite "SELECT COUNT(*) FROM transformations;"

# Voir les dernières transformations
sqlite3 ../ratecard-dump/ratecard.sqlite "SELECT id, carrier, status FROM transformations ORDER BY created_at DESC LIMIT 5;"
```

---

## 🐛 Débogage

### Activer les logs détaillés

```bash
# Avec uvicorn
uvicorn app.main:app --log-level debug

# Dans pytest
pytest --log-cli-level=DEBUG
```

### Voir les requêtes SQL

Ajoutez dans `app/core/db/session.py` :

```python
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True  # ← Active les logs SQL
)
```

### Inspecter la base de données

```bash
# Lancer SQLite en mode interactif
sqlite3 ../ratecard-dump/ratecard.sqlite

# Commandes utiles
.tables              # Lister les tables
.schema transformations  # Voir le schéma
SELECT * FROM transformations LIMIT 5;  # Voir les données
```

---

## ✅ Checklist de test complète

Avant de déployer en production, vérifiez :

- [ ] Tous les tests pytest passent (`pytest`)
- [ ] Couverture de code > 90% (`pytest --cov`)
- [ ] Tests manuels Swagger fonctionnent
- [ ] Script test_api.sh passe sans erreurs
- [ ] Validation des fichiers (extensions)
- [ ] Gestion d'erreurs (404, 500)
- [ ] Pagination fonctionne correctement
- [ ] Filtres (carrier, date, status) fonctionnent
- [ ] Rollback automatique en cas d'erreur
- [ ] Timestamps en UTC
- [ ] JSON corrompu géré gracieusement

---

## 📚 Ressources

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **Documentation pytest** : https://docs.pytest.org/
- **FastAPI Testing** : https://fastapi.tiangolo.com/tutorial/testing/

---

## 🆘 Problèmes courants

### Erreur : "Database session cannot be None"

**Solution** : Vérifiez que l'injection de dépendance fonctionne correctement dans les routes.

### Erreur : "Table transformations already exists"

**Solution** : La table existe déjà. Pas besoin de réinitialiser.

### Tests échouent : "No module named 'app'"

**Solution** : Lancez pytest depuis la racine du projet.

### Port 8000 déjà utilisé

**Solution** :
```bash
# Trouver le processus
lsof -i :8000

# Utiliser un autre port
uvicorn app.main:app --port 8001
```
