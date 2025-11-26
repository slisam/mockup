# Use official lightweight Python image
FROM python:3.11-slim

# Ensure Python output is unbuffered
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Install system dependencies (SQLite + others)
RUN apt-get update && apt-get install -y \
    sqlite3 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Expose API port
EXPOSE 8000

# Default command (Cloud Run uses this)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]