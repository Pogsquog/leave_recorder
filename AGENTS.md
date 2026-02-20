# AGENTS.md

Instructions for AI agents working on this codebase.

## Project Overview

Holiday Holliday - A simple web app for recording/booking leave.

## Technology Stack

- **Backend**: Django 5.x + Django REST Framework + Django Channels
- **Frontend**: Django templates + HTMX + Alpine.js
- **Database**: PostgreSQL (production), SQLite (testing/local dev)
- **Cache/Channels**: Redis
- **Deployment**: Azure Container Apps

## Commands

### Local Development

```bash
# Setup development environment
./scripts/setup.sh

# Run development server (SQLite)
./scripts/run.sh

# Run tests
./scripts/test.sh

# Run linting/formatting/security checks
./scripts/lint.sh
```

### Docker

```bash
# Run in Docker (PostgreSQL + Redis)
./scripts/docker-run.sh

# Run tests in Docker
./scripts/docker-test.sh
```

### Django Management Commands

```bash
# Create superuser
source .venv/bin/activate
python manage.py createsu

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
```

## Code Style

- Use ruff for linting and formatting
- Line length: 120 characters
- Target Python: 3.11+
- No comments unless explicitly requested

## Testing

- pytest with pytest-django
- Tests in `tests/` directory
- Settings: `config.settings.test`

## Project Structure

```
apps/
  users/          # User model, preferences, auth
  leave/          # Leave entries, calculations
  organisations/  # Orgs, membership, invites
  api/            # REST API, API keys
config/
  settings/       # prod.py, test.py
  urls.py
  asgi.py
  wsgi.py
templates/        # Django templates
static/           # CSS, JS
tests/            # Test files
scripts/          # Shell scripts
```
