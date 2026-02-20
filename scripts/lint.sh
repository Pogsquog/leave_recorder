#!/bin/bash
set -e

echo "=== Running code quality checks ==="

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install dependencies
pip install -q -r requirements.txt

echo ""
echo "=== Ruff linting ==="
ruff check .

echo ""
echo "=== Ruff format check ==="
ruff format --check .

echo ""
echo "=== Bandit security check ==="
bandit -r apps config --skip B101

echo ""
echo "=== pip-audit (CVE check) ==="
pip-audit --requirement requirements.txt

echo ""
echo "=== All checks passed! ==="
