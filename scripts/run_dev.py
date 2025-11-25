#!/usr/bin/env python3
"""Start the FastAPI application in development mode.

Run this from the project root: python scripts/run_dev.py
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Force local mode to avoid GCS dependency
os.environ['MODE'] = 'local'

if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting FastAPI server in development mode...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🔄 Auto-reload enabled")
    print("\nPress CTRL+C to stop\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
