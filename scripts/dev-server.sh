#!/bin/bash
# Development server for manual testing
# Uses port 8765 (tests use port 8766 to avoid conflicts)

set -e

cd "$(dirname "$0")/.."

echo "Starting dev server on http://0.0.0.0:8765"
echo "Press Ctrl+C to stop"
echo ""

uvicorn great_dictator.app:app --host 0.0.0.0 --port 8765 --reload
