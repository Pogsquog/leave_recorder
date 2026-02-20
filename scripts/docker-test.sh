#!/bin/bash
set -e

echo "=== Running tests in Docker ==="

# Build test image
echo "Building test container..."
docker compose build app

echo ""
echo "Running tests in container..."
docker compose run --rm app bash -c "
    set -e
    echo '=== Running ruff linting ==='
    ruff check .
    
    echo ''
    echo '=== Running ruff format check ==='
    ruff format --check .
    
    echo ''
    echo '=== Running bandit security check ==='
    bandit -r apps config --skip B101
    
    echo ''
    echo '=== Running pytest ==='
    DJANGO_SETTINGS_MODULE=config.settings.test SECRET_KEY=test-secret-key pytest --tb=short -v
    
    echo ''
    echo '=== All tests passed! ==='
"

echo ""
echo "Stopping containers..."
docker compose down
