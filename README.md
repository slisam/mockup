# Rate Cards Transformation API — Modules renommés (sémantique métier)

Cette archive reprend la structure de ton projet initial mais **renomme les modules**
`message.py` en **`transformations.py`** dans `api/routes`, `models`, `schemas`, `services`.

## Démarrage
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp env.local/.env.local .env  # ou env.production/.env
uvicorn app.main:app --reload
```
