
#!/usr/bin/env bash
set -e

echo "=== Initializing local Transformations History DB ==="

# 1) Resolve project root so the DB sits beside FastAPI app code
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
echo "Project root: $PROJECT_ROOT"

# 2) Choose a single canonical DB file used by FastAPI (align with app.core.db.session)
# NOTE: We intentionally use a plain filesystem path that sqlite3 understands.
DB_FILE="$PROJECT_ROOT/transformations_history.db"
echo "SQLite DB path: $DB_FILE"

# 3) Create the SQLite DB file if it does not exist
if [ ! -f "$DB_FILE" ]; then
  # Create empty DB and run VACUUM to initialize file structure
  sqlite3 "$DB_FILE" "VACUUM;"
  echo "Created SQLite DB: $DB_FILE"
else
  echo "SQLite DB already exists: $DB_FILE"
fi

# 4) Apply schema (DDL) for transformations_history table
# NOTE: id is TEXT PRIMARY KEY because app model uses 'id: str'
DDL=$(cat <<'SQL'
CREATE TABLE IF NOT EXISTS transformation_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  transformation_id TEXT NOT NULL,
  status TEXT NOT NULL,
  carrier TEXT,
  trade_lane TEXT,
  timestamp TEXT NOT NULL,
  details TEXT,            -- JSON string
  file_names TEXT          -- JSON string of {"xlsx_name": "...", "docx_name": "..."}
);
SQL
)

echo "Applying DDL..."
sqlite3 "$DB_FILE" "$DDL"
echo "DDL applied."

# 5) Optional: seed a sample row to quickly test SELECT/DELETE in dev
# NOTE: Keep it minimal; you can remove this block if you prefer a clean DB.
SEED_ID="seed-0001"
EXISTS=$(sqlite3 "$DB_FILE" "SELECT COUNT(1) FROM transformations_history WHERE id='$SEED_ID';")

if [ "$EXISTS" = "0" ]; then
  echo "Seeding one sample row..."
  sqlite3 "$DB_FILE" \
    "INSERT INTO transformations_history (id, created_at, status, carrier, trade_lane, file_names)
     VALUES ('$SEED_ID', datetime('now'), 'IN_PROGRESS', 'CarrierSeed', 'EU-APAC', '{\"excel\":\"sample.xlsx\",\"word\":\"sample.docx\"}');"
  echo "Seeded: $SEED_ID"
else
  echo "Sample row already present: $SEED_ID (skip)"
fi

echo "=== Local Transformations History DB is ready ==="
