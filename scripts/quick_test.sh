#!/bin/bash
# Quick test script
MODE=local python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

sleep 3

echo "Testing endpoints..."
echo ""

echo "1. Root endpoint:"
curl -s http://localhost:8000/ | python -m json.tool

echo ""
echo "2. OpenAPI schema:"
curl -s http://localhost:8000/openapi.json | python -m json.tool | head -30

echo ""
echo "3. List transformations:"
curl -s http://localhost:8000/transformations | python -m json.tool

kill $SERVER_PID 2>/dev/null
