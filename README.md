```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp env.local/.env.local .env  # ou env.production/.env
uvicorn app.main:app --reload
```
