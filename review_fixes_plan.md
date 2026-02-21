# Code Review - Fixes Plan

**Review Date:** February 20, 2026
**Project:** Holiday Holliday
**Reviewer:** Qwen Code

---

## Executive Summary

The Holiday Holliday project is well-structured and implements most core features correctly. This review identified **26 issues** across security, code quality, missing features, testing, and deployment categories.

**Completed:** 26 issues (#1-#26)
**Remaining:** 0 issues

### Priority Legend

| Priority | Description | Timeline |
|----------|-------------|----------|
| 🔴 P0 | Critical - Fix Immediately | Within 24 hours |
| 🟠 P1 | High - Fix Soon | Within 1 week |
| 🟡 P2 | Medium - Plan to Fix | Within 1 month |
| 🟢 P3 | Low - Nice to Have | As time permits |

---

## 🟡 P2 - Medium Priority Code Quality

### 8. Magic Numbers in Templates ✅

**Status:** COMPLETED

**File:** `apps/leave/templatetags/calendar_tags.py`
**Issue:** Week day calculation hardcoded

**Fix:** Created template tag `get_weekday_name` that returns translated weekday names based on week start preference.

**Estimated Effort:** 1 hour

---

### 9. Inconsistent Error Handling in API ✅

**Status:** COMPLETED

**File:** `apps/api/exceptions.py`
**Issue:** Mixed error response patterns

**Fix:** Created custom exception handler that standardizes error responses with consistent format:
```python
{
    "error": True,
    "message": "...",
    "status_code": 400,
}
```

Configured in `REST_FRAMEWORK` settings.

**Estimated Effort:** 1 hour

---

### 10. Add Consistent Type Hints ✅

**Status:** COMPLETED

**Files:** All views, models, and utilities
**Issue:** Inconsistent type hinting

**Fix:** Added type hints to all function signatures in:
- `apps/api/views.py`
- `apps/leave/models.py`
- `apps/leave/views.py`
- `apps/organisations/models.py`

**Estimated Effort:** 2 hours

---

### 11. Use Django TextChoices Instead of StrEnum ✅

**Status:** COMPLETED

**Files:** `apps/leave/models.py`, `apps/organisations/models.py`
**Issue:** Manual choices conversion

**Fix:** Already using Django TextChoices:
```python
class LeaveType(models.TextChoices):
    VACATION = "vacation", _("Vacation")
    SICK = "sick", _("Sick")
```

**Estimated Effort:** 1 hour

---

### 13. Add Pagination to API ✅

**Status:** COMPLETED

**File:** `config/settings/prod.py`
**Issue:** Leave entries return all results

**Fix:** Already configured:
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
}
```

**Estimated Effort:** 20 minutes

---

### 14. Database Configuration for Production ✅

**Status:** COMPLETED

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

Production now uses PostgreSQL by default with environment variable configuration.
Test settings use SQLite unless `DATABASE_URL` is explicitly set.

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

### 16. Structured Logging for Production ✅

**Status:** COMPLETED

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

JSON logging enabled when `PRODUCTION` environment variable is set.

**Estimated Effort:** 30 minutes

---

### 17. API Documentation Enhancements ✅

**Status:** COMPLETED

**File:** `apps/api/views.py`

**Fix:** Added drf-spectacular documentation to all API endpoints:
- `LeaveEntryViewSet` - List, create, retrieve, update, delete with parameter docs
- `OrganisationViewSet` - List, retrieve, members, leave_entries endpoints
- `current_user` - GET/PATCH user profile
- `api_keys` - GET/POST/DELETE API key management

**Estimated Effort:** 2 hours

---

### 18. Timezone Handling Consistency ✅

**Status:** COMPLETED

**Files:** Throughout codebase
**Issue:** Mixed use of `datetime.now()` and `timezone.now()`

**Fix:** Verified all code uses `timezone.now()` - no `datetime.now()` instances found.

**Estimated Effort:** 1 hour

---

### 19. Complete i18n Support ✅

**Status:** COMPLETED

**Files:** `config/settings/prod.py`, `templates/base.html`

**Fix:**
- Extended `LANGUAGES` to include German, French, Spanish, and Italian
- Added language selector dropdown to base template navigation
- LocaleMiddleware already configured
- i18n URLs already included

**Estimated Effort:** 4 hours

---

### 20. Backup Strategy Documentation ✅

**Status:** COMPLETED

**File:** `docs/backup.md`

Document:
- Azure Database backup configuration
- Manual backup scripts
- Recovery procedures
- Disaster recovery plan
- Backup schedule recommendations
- Testing procedures

**Estimated Effort:** 2 hours

---

### 21. Add .gitignore Entries ✅

**Status:** COMPLETED

**File:** `.gitignore`

**Fix:** Already has all recommended entries:
- Environment files (.env, .env.local, etc.)
- Database files (db.sqlite3, etc.)
- IDE files (.idea/, .vscode/, etc.)
- Testing files (.pytest_cache/, .coverage, etc.)

**Estimated Effort:** 10 minutes

---

## 🟠 P1 - Testing Gaps

### 22. Add Organisation Tests ✅

**Status:** COMPLETED

**File:** `tests/test_organisations.py`

Test coverage:
- Organisation creation and slug uniqueness
- Organisation membership creation and roles
- Invite creation, expiration, and acceptance
- Organisation views (list, detail, create, invite)
- Organisation leave entries retrieval

**Estimated Effort:** 4 hours

---

### 23. Add Signal Handler Tests ✅

**Status:** COMPLETED

**File:** `tests/test_signals.py`

Test coverage:
- Leave entry created triggers notification
- Leave entry updated triggers notification
- Leave entry deleted triggers notification
- Signal fails silently when channel layer unavailable
- WebSocket message format verification

**Estimated Effort:** 2 hours

---

### 24. Add WebSocket Consumer Tests ✅

**Status:** COMPLETED

**File:** `tests/test_websocket.py`

Test coverage:
- Connection authentication
- Group subscription on connect
- Group removal on disconnect
- Message reception
- Multiple users in same organisation group

**Estimated Effort:** 2 hours

---

### 25. Add Integration Tests ✅

**Status:** COMPLETED

**File:** `tests/test_integration.py`

Test full API workflows:
- User registration → create leave → view stats
- Organisation invite → accept → view shared leave
- API key creation → authenticated requests
- Leave entry CRUD via API
- Organisation API endpoints
- Current user API endpoint

**Estimated Effort:** 4 hours

---

### 26. Add Edge Case Tests for LeaveCalculator ✅

**Status:** COMPLETED

**File:** `tests/test_leave_edge_cases.py`

Additional test cases:
- Year boundary calculations
- Carryover edge cases
- Different year start dates
- Leap year handling (Feb 29)
- Half-day entries at year boundaries
- Negative remaining days (over allowance)
- Zero allowance edge case
- Mixed leave types
- Future booked days calculation
- Month data with/without entries
- Additional users in month view
- Prev/next month calculations across years
- Days until year end calculation

**Estimated Effort:** 3 hours

---

## Implementation Order

### Phase 1: Code Quality (Remaining) ✅ COMPLETED
8. Template magic numbers (#8) ✅
9. Error handling (#9) ✅
10. Type hints (#10) ✅

### Phase 2: Testing ✅ COMPLETED
22. Organisation tests (#22) ✅
23. Signal tests (#23) ✅
24. WebSocket tests (#24) ✅
25. Integration tests (#25) ✅
26. Edge case tests (#26) ✅

### Phase 3: Features & Polish ✅ COMPLETED
17. API docs (#17) ✅
18. Timezone handling (#18) ✅
19. i18n support (#19) ✅
20. Backup docs (#20) ✅
21. .gitignore (#21) ✅

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
| `templatetags/calendar_tags.py` | Calendar template tags | 🟡 P2 | ✅ Created |
| `apps/api/exceptions.py` | Custom exception handler | 🟡 P2 | ✅ Created |
| `apps/core/views.py` | Health check endpoints | 🟢 P3 | ✅ Created |
| `tests/test_organisations.py` | Organisation tests | 🟠 P1 | ✅ Created |
| `tests/test_signals.py` | Signal tests | 🟠 P1 | ✅ Created |
| `tests/test_websocket.py` | WebSocket tests | 🟠 P1 | ✅ Created |
| `tests/test_integration.py` | Integration tests | 🟠 P1 | ✅ Created |
| `docs/backup.md` | Backup documentation | 🟢 P3 | ✅ Created |
| `tests/test_leave_edge_cases.py` | Edge case tests | 🟠 P1 | ✅ Created |

---

## Total Estimated Effort

| Phase | Hours |
|-------|-------|
| Phase 1: Code Quality (Remaining) | 3.5 hours |
| Phase 2: Testing | 15 hours |
| Phase 3: Features & Polish | 9.5 hours |
| **Total Remaining** | **28 hours** |

**Actual Time:** All issues completed!

---

## Notes

- All estimates assume a developer familiar with Django and the codebase
- Testing phase may take longer depending on test complexity
- Some fixes may reveal additional issues during implementation
- Consider running linting (`./scripts/lint.sh`) after each phase

**All 26 issues have been successfully resolved!** 🎉
