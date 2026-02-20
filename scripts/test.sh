#!/bin/bash
set -e

echo "=== Running tests locally ==="

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Set environment variables
export DJANGO_SETTINGS_MODULE=config.settings.test
export SECRET_KEY=test-secret-key

echo ""
echo "=== Running ruff linting ==="
ruff check .

echo ""
echo "=== Running ruff format check ==="
ruff format --check .

echo ""
echo "=== Running bandit security check ==="
bandit -r apps config --skip B101

echo ""
echo "=== Running pytest ==="
pytest --tb=short -v

echo ""
echo "=== All tests passed! ==="
