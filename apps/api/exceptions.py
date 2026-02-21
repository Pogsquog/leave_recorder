"""Custom exception handler for consistent API error responses."""

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Handle exceptions and return consistent error response format.

    Args:
        exc: The exception raised
        context: The context in which the exception was raised

    Returns:
        Response object with standardized error format

    """
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "error": True,
            "message": response.data.get("detail", str(response.data)),
            "status_code": response.status_code,
        }

    return response
