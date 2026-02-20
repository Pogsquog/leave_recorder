# Code Review - Fixes Plan

**Review Date:** February 20, 2026
**Project:** Holiday Holliday
**Reviewer:** Qwen Code

---

## Executive Summary

The Holiday Holliday project is well-structured and implements most core features correctly. This review identified **26 issues** across security, code quality, missing features, testing, and deployment categories.

**Completed:** 11 issues (#1-#7, #11, #12, #13, #15)
**Remaining:** 15 issues

### Priority Legend

| Priority | Description | Timeline |
|----------|-------------|----------|
| 🔴 P0 | Critical - Fix Immediately | Within 24 hours |
| 🟠 P1 | High - Fix Soon | Within 1 week |
| 🟡 P2 | Medium - Plan to Fix | Within 1 month |
| 🟢 P3 | Low - Nice to Have | As time permits |

---

## 🟡 P2 - Medium Priority Code Quality

### 8. Magic Numbers in Templates

**File:** `templates/leave/month.html:32-44`  
**Issue:** Week day calculation hardcoded

**Fix:** Create template tag `templatetags/calendar_tags.py`:

```python
from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()

@register.simple_tag
def get_weekday_name(day_number: int, week_start: int = 1) -> str:
    """Get translated weekday name based on week start preference."""
    days_monday_start = [_("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat"), _("Sun")]
    days_sunday_start = [_("Sun"), _("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat")]
    
    if week_start == 1:
        return days_monday_start[day_number - 1]
    return days_sunday_start[day_number - 1]
```

**Estimated Effort:** 1 hour

---

### 9. Inconsistent Error Handling in API

**File:** `apps/api/views.py`  
**Issue:** Mixed error response patterns

**Fix:** Create custom exception handler `apps/api/exceptions.py`:

```python
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'error': True,
            'message': response.data.get('detail', str(response.data)),
            'status_code': response.status_code,
        }
    
    return response
```

Then configure in settings:
```python
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'apps.api.exceptions.custom_exception_handler',
}
```

**Estimated Effort:** 1 hour

---

### 10. Add Consistent Type Hints

**Files:** All views, models, and utilities  
**Issue:** Inconsistent type hinting

**Fix:** Add type hints to all function signatures:

```python
from typing import Optional, List, Dict, Any
from datetime import date

def get_year_stats(user: User, year: Optional[int] = None) -> Dict[str, Any]:
    # ... implementation
```

**Estimated Effort:** 2 hours

---

### 11. Use Django TextChoices Instead of StrEnum

**Files:** `apps/leave/models.py`, `apps/organisations/models.py`  
**Issue:** Manual choices conversion

**Fix:**
```python
from django.db import models

class LeaveType(models.TextChoices):
    VACATION = "vacation", "Vacation"
    SICK = "sick", "Sick Leave"

# Usage
leave_type = models.CharField(
    max_length=20,
    choices=LeaveType.choices,
    default=LeaveType.VACATION,
)
```

**Estimated Effort:** 1 hour

---

### 13. Add Pagination to API

**File:** `apps/api/views.py`  
**Issue:** Leave entries return all results

**Fix:**
```python
# In settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'MAX_LIMIT': 1000,
}
```

**Estimated Effort:** 20 minutes

---

### 14. Database Configuration for Production

**File:** `config/settings/prod.py`  
**Issue:** SQLite default in production settings

**Fix:**
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_NAME", "holiday_holliday"),
        "USER": os.environ.get("POSTGRES_USER", "holiday"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# Fallback to DATABASE_URL if provided
database_url = os.environ.get("DATABASE_URL")
if database_url:
    import dj_database_url
    DATABASES["default"] = dj_database_url.parse(database_url)
```

**Estimated Effort:** 45 minutes

---

## 🟢 P3 - Low Priority Improvements

### 15. Add Health Check Endpoints ✅

**Status:** COMPLETED

**File:** New file `apps/core/views.py`

```python
from django.http import JsonResponse
from django.db import connection

def healthz(request):
    """Return basic health check for liveness probes."""
    return JsonResponse({"status": "ok"})

def ready(request):
    """Return readiness check including database connectivity."""
    try:
        connection.ensure_connection()
        return JsonResponse({"status": "ready", "database": "ok"})
    except Exception as e:
        return JsonResponse({"status": "not ready", "database": str(e)}, status=503)
```

Endpoints available at `/healthz` and `/ready`.

**Estimated Effort:** 30 minutes

---

### 16. Structured Logging for Production

**File:** `config/settings/prod.py`

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
```

**Estimated Effort:** 30 minutes

---

### 17. API Documentation Enhancements

**File:** `apps/api/views.py`

```python
from drf_spectacular.utils import extend_schema, OpenApiParameter

@extend_schema(
    parameters=[
        OpenApiParameter(
            name="start_date",
            description="Filter by start date (ISO format)",
            required=False,
            type=str,
        ),
    ],
    responses={200: LeaveEntrySerializer(many=True)},
)
def list(self, request, *args, **kwargs):
    # ... existing code
```

**Estimated Effort:** 2 hours

---

### 18. Timezone Handling Consistency

**Files:** Throughout codebase  
**Issue:** Mixed use of `datetime.now()` and `timezone.now()`

**Fix:** Replace all `datetime.now()` with `timezone.now()`:

```python
from django.utils import timezone

# Instead of: created_at = datetime.now()
# Use: created_at = timezone.now()
```

**Estimated Effort:** 1 hour

---

## 🟡 P2 - Missing Features

### 19. Complete i18n Support

**Files:** `config/settings/prod.py`, templates, views

**Fix:**
```python
# Add to settings
LANGUAGES = [
    ("en", "English"),
    ("de", "German"),
    ("fr", "French"),
    # Add more as needed
]

LOCALE_MIDDLEWARE_EXCLUDED = [
    "django.middleware.locale.LocaleMiddleware",
]
```

Add language selector to base template and document translation process in README.

**Estimated Effort:** 4 hours

---

### 20. Backup Strategy Documentation

**File:** New file `docs/backup.md`

Document:
- Azure Database backup configuration
- Manual backup scripts
- Recovery procedures

**Estimated Effort:** 2 hours

---

### 21. Add .gitignore Entries

**File:** `.gitignore`

```gitignore
# Environment
.env
.env.local
.env.*.local

# Database
db.sqlite3
*.db

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
```

**Estimated Effort:** 10 minutes

---

## 🟠 P1 - Testing Gaps

### 22. Add Organisation Tests

**File:** `tests/test_organisations.py` (new)

Test coverage needed:
- Organisation creation
- Invite flow (create, accept, expire)
- Membership permissions
- Organisation leave view

**Estimated Effort:** 4 hours

---

### 23. Add Signal Handler Tests

**File:** `tests/test_signals.py` (new)

Test coverage needed:
- Leave entry created triggers notification
- Leave entry deleted triggers notification
- WebSocket message format

**Estimated Effort:** 2 hours

---

### 24. Add WebSocket Consumer Tests

**File:** `tests/test_websocket.py` (new)

Test coverage needed:
- Connection authentication
- Group subscription
- Message reception

**Estimated Effort:** 2 hours

---

### 25. Add Integration Tests

**File:** `tests/test_integration.py` (new)

Test full API workflows:
- User registration → create leave → view stats
- Organisation invite → accept → view shared leave
- API key creation → authenticated requests

**Estimated Effort:** 4 hours

---

### 26. Add Edge Case Tests for LeaveCalculator

**File:** `tests/test_leave.py`

Additional test cases:
- Year boundary calculations
- Carryover edge cases
- Different year start dates
- Leap year handling

**Estimated Effort:** 3 hours

---

## Implementation Order

### Phase 1: Code Quality (Remaining)
8. Template magic numbers (#8)
9. Error handling (#9)
10. Type hints (#10)
11. TextChoices (#11)
13. Pagination (#13)
14. Database config (#14)

### Phase 2: Testing
22. Organisation tests (#22)
23. Signal tests (#23)
24. WebSocket tests (#24)
25. Integration tests (#25)
26. Edge case tests (#26)

### Phase 3: Features & Polish
16. Structured logging (#16)
17. API docs (#17)
18. Timezone handling (#18)
19. i18n support (#19)
20. Backup docs (#20)
21. .gitignore (#21)

---

## Quick Reference

### Files Requiring Changes

| File | Issues | Priority |
|------|--------|----------|
| `config/settings/prod.py` | #14, #16 | 🟡 P2, 🟢 P3 |
| `apps/api/views.py` | #13, #17 | 🟡 P2 |
| `apps/leave/views.py` | #7 | 🟡 P2 |
| `apps/leave/models.py` | #11 | 🟡 P2 |
| `templates/leave/month.html` | #8 | 🟡 P2 |
| `.gitignore` | #21 | 🟢 P3 |

### New Files to Create

| File | Purpose | Priority | Status |
|------|---------|----------|--------|
| `templatetags/calendar_tags.py` | Calendar template tags | 🟡 P2 | Pending |
| `apps/api/exceptions.py` | Custom exception handler | 🟡 P2 | Pending |
| `apps/core/views.py` | Health check endpoints | 🟢 P3 | ✅ Created |
| `tests/test_organisations.py` | Organisation tests | 🟠 P1 | Pending |
| `tests/test_signals.py` | Signal tests | 🟠 P1 | Pending |
| `tests/test_websocket.py` | WebSocket tests | 🟠 P1 | Pending |
| `tests/test_integration.py` | Integration tests | 🟠 P1 | Pending |
| `docs/backup.md` | Backup documentation | 🟢 P3 | Pending |

---

## Total Estimated Effort

| Phase | Hours |
|-------|-------|
| Phase 1: Code Quality (Remaining) | 5.5 hours |
| Phase 2: Testing | 15 hours |
| Phase 3: Features & Polish | 10 hours |
| **Total Remaining** | **30.5 hours** |

---

## Notes

- All estimates assume a developer familiar with Django and the codebase
- Testing phase may take longer depending on test complexity
- Some fixes may reveal additional issues during implementation
- Consider running linting (`./scripts/lint.sh`) after each phase
