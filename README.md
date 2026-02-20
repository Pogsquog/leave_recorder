# Holiday Holliday

A simple web application for recording and booking leave.

## Features

- Month view calendar with leave tracking
- Click to add leave, right-click for half days, drag to select date ranges
- Supports vacation and sick leave
- Track total allowance, taken days, booked days, and remaining days
- Organisation support with shared visibility between members
- Invite mechanism for team collaboration
- REST API with API key authentication
- Internationalization support

## Tech Stack

- **Backend**: Django 5.x + Django REST Framework + Django Channels
- **Frontend**: Django templates + HTMX + Alpine.js
- **Database**: PostgreSQL (production), SQLite (development)
- **Cache/Real-time**: Redis
- **Deployment**: Azure Container Apps

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (optional, SQLite for local dev)
- Redis (optional, for real-time features)

### Local Development

```bash
# Setup development environment
./scripts/setup.sh

# Run development server
./scripts/run.sh
```

Visit http://localhost:8000

### Docker

```bash
# Run with Docker
./scripts/docker-run.sh

# Run tests in Docker
./scripts/docker-test.sh
```

### Running Tests

```bash
# Run tests with Redis (recommended - all tests pass)
./scripts/test-with-redis.sh

# Run tests without Redis (some API tests will fail)
./scripts/test.sh
```

The `test-with-redis.sh` script automatically starts a Redis container before running tests and cleans it up afterwards.

### Linting

```bash
./scripts/lint.sh
```

### Duplicate Code Detection

```bash
./scripts/dupcheck.sh
```

Uses [jscpd](https://github.com/kucherenko/jscpd) to detect code duplication across the codebase.
Configured to scan Python, JavaScript, HTML, CSS, JSON, YAML, and Markdown files.

## Configuration

Environment variables:

- `SECRET_KEY` - Django secret key
- `DEBUG` - Set to "true" for development
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `DATABASE_URL` - PostgreSQL connection URL
- `REDIS_URL` - Redis connection URL for channels

## REST API

API documentation is available at `/api/docs/` when running the server.

Generate an API key in your user preferences to authenticate.

## License

AGPL / Commercial

## Author

Stuart Holliday
