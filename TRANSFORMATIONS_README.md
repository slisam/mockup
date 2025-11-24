# Transformations API - SQLAlchemy Implementation

## Vue d'ensemble

Cette implémentation utilise SQLAlchemy pour gérer les transformations dans une base de données SQLite (ou PostgreSQL si nécessaire).

## Changements effectués

### 1. Modèle SQLAlchemy (`app/models/transformations.py`)

- Création d'un modèle `Transformation` avec SQLAlchemy
- Colonnes principales :
  - `id` : Identifiant unique (UUID)
  - `created_at` : Date de création
  - `status` : Statut de la transformation
  - `carrier` : Transporteur
  - `trade_lane` : Route commerciale
  - `xlsx_name`, `docx_name` : Noms des fichiers
  - `transformation_data` : Données complètes au format JSON
  - `progress`, `message` : Suivi de progression
  - `status_details` : Détails du statut au format JSON

### 2. Service de transformations (`app/services/transformations.py`)

- `create_transformation()` : Crée et enregistre une transformation dans la BD
- `list_transformations()` : Liste les transformations avec filtrage et pagination cursor-based
- `get_status_details()` : Récupère les détails de statut d'une transformation

### 3. Routes API (`app/api/routes/transformations.py`)

- Mise à jour pour injecter la session de base de données via dependency injection
- Utilisation de `get_db()` pour obtenir une session SQLAlchemy

### 4. Configuration de la base de données (`app/core/db/session.py`)

- Import conditionnel de GCS pour éviter les erreurs en mode local
- Support du mode local et cloud (GCS)

## Initialisation de la base de données

Pour créer la table des transformations :

```bash
python scripts/init_db.py
```

Cela créera la table `transformations` dans la base de données SQLite.

## Vérification de la structure

Pour vérifier la structure de la base de données :

```bash
python scripts/check_db.py
```

## Utilisation de l'API

### Créer une transformation

```bash
POST /transformations
Content-Type: multipart/form-data

- excel_file: fichier .xlsx ou .xls
- word_file: fichier .docx ou .doc
- data: JSON contenant TransformationInput
```

### Lister les transformations

```bash
GET /transformations?cursor=...&limit=20&date.start=2024-01-01&carrier=MSC&status=IN_PROGRESS
```

### Obtenir les détails de statut

```bash
GET /transformations/{id}/status-details-in-progress
```

## Avantages de cette implémentation

1. **Type-safe** : Utilisation de SQLAlchemy avec des types définis
2. **Flexible** : Facile de migrer vers PostgreSQL ou MySQL
3. **Maintenable** : Code clair et bien structuré
4. **Pagination efficace** : Pagination cursor-based pour de meilleures performances
5. **Filtrage avancé** : Support de multiples filtres (date, carrier, trade_lane, status)

## Notes techniques

- Les données JSON sont stockées dans des colonnes TEXT
- Les index sont créés sur les colonnes fréquemment utilisées (id, status, carrier, trade_lane)
- La pagination utilise le timestamp `created_at` comme cursor
- Génération automatique d'UUID pour les IDs
