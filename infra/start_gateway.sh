#!/bin/bash
set -e

echo "🚀 Starting Relay Gateway..."

# Initialize policies from S3
echo "📚 Initializing OPA policies..."
python3 gateway/init_policies.py

# Start the Gateway
echo "✅ Starting Gateway service..."
exec python -m uvicorn gateway.main:app --host 0.0.0.0 --port 8000
