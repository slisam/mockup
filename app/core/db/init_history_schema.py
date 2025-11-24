
import os
import sqlite3

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DB_FILE = os.path.join(PROJECT_ROOT, "transformations_history.db")

DDL = """
CREATE TABLE IF NOT EXISTS transformation_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  transformation_id TEXT NOT NULL,
  status TEXT NOT NULL,
  carrier TEXT,
  trade_lane TEXT,
  timestamp TEXT NOT NULL,
  details TEXT,
  file_names TEXT
);
"""

def main():
    # Ensure parent directory exists
    parent = os.path.dirname(DB_FILE)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
    try:
        conn.executescript(DDL)
        conn.commit()
        print(f"Schema initialized at: {DB_FILE}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
