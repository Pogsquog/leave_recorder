#!/bin/bash
set -e

echo "=== Setting up development environment ==="

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "=== Setup complete! ==="
echo ""
echo "To run the development server:"
echo "  ./scripts/run.sh"
echo ""
echo "To run tests:"
echo "  ./scripts/test.sh"
echo ""
echo "To create a superuser:"
echo "  source .venv/bin/activate && python manage.py createsu"
