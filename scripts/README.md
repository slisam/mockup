# Scripts Utilitaires

Scripts de développement et de maintenance pour le projet.

## Scripts disponibles

### init_db.py

Initialise les tables de la base de données SQLite.

```bash
python scripts/init_db.py
```

Ce script crée toutes les tables définies dans les modèles SQLAlchemy.

### check_db.py

Affiche la structure de la base de données et les schémas des tables.

```bash
python scripts/check_db.py
```

Utile pour vérifier que les migrations ont été correctement appliquées.

## Notes

- Ces scripts forcent le mode `local` pour éviter les dépendances GCS
- Ils doivent être exécutés depuis la racine du projet
- La base de données est créée dans `../ratecard-dump/ratecard.sqlite`
