#!/bin/bash
set -e

echo "=== Running jscpd (Copy/Paste Detector) ==="

# Check if jscpd is installed
if ! command -v jscpd &> /dev/null; then
    echo "jscpd not found. Installing..."
    npm install -g jscpd
fi

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Create a temporary jscpd config file
CONFIG_FILE="$PROJECT_ROOT/.jscpd.json"

cat > "$CONFIG_FILE" << 'EOF'
{
  "threshold": 10,
  "reporters": ["console"],
  "ignore": [
    "**/node_modules/**",
    "**/.venv/**",
    "**/venv/**",
    "**/__pycache__/**",
    "**/*.pyc",
    "**/.git/**",
    "**/staticfiles/**",
    "**/migrations/**",
    "**/uv.lock",
    "**/package-lock.json",
    "**/yarn.lock",
    "**/*.min.js",
    "**/*.min.css",
    "**/*.svg",
    "**/locale/**"
  ],
  "minLines": 5,
  "minTokens": 50,
  "formats": ["python", "javascript", "typescript", "html", "css", "json", "yaml", "markdown"],
  "path": ["apps", "config", "templates", "static", "tests", "scripts"]
}
EOF

echo ""
echo "Scanning project for duplicate code..."
echo "Project root: $PROJECT_ROOT"
echo "Config: $CONFIG_FILE"
echo ""

# Run jscpd with config file
jscpd --config "$CONFIG_FILE" "$PROJECT_ROOT"

# Capture exit code
EXIT_CODE=$?

# Clean up config file
rm -f "$CONFIG_FILE"

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "=== Duplicate check complete - No significant duplicates found ==="
else
    echo "=== Duplicate check complete - Duplicates detected (see above) ==="
fi

exit $EXIT_CODE
