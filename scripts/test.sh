#!/bin/bash
# Test script for Agent Lucky

set -e

echo "🧪 Running Agent Lucky tests..."

# Backend tests
echo "Testing backend..."
cd backend
python -m pytest tests/ -v

echo "✅ All tests passed!"

