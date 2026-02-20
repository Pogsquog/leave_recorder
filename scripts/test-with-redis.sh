#!/bin/bash
set -e

echo "=== Running tests locally with Redis ==="

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
export REDIS_URL=redis://localhost:6379/0

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH"
    echo "Please install Docker or run tests using ./scripts/docker-test.sh"
    exit 1
fi

# Start Redis container
echo "Starting Redis container..."
CONTAINER_NAME="holiday-holliday-redis-test"

# Remove any existing container with the same name
docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1 || true

# Start Redis
docker run -d --name "$CONTAINER_NAME" -p 6379:6379 redis:7-alpine > /dev/null

echo "Waiting for Redis to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=0
while ! docker exec "$CONTAINER_NAME" redis-cli ping > /dev/null 2>&1; do
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
        echo "ERROR: Redis failed to start within timeout"
        docker logs "$CONTAINER_NAME"
        docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1
        exit 1
    fi
    sleep 0.5
done
echo "Redis is ready!"

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping Redis container..."
    docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1 || true
}

# Trap to ensure cleanup runs on exit
trap cleanup EXIT

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
