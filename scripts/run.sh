#!/bin/bash
set -e

echo "=== Running Holiday Holliday locally ==="

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

# Run migrations if needed
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run development server
echo ""
echo "Starting development server at http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""
python manage.py runserver 0.0.0.0:8000
