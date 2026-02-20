from django.db import connection
from django.http import JsonResponse


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
