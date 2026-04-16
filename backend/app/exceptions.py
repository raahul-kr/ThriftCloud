"""
Custom exception handlers for ThriftCloud API.
"""

from fastapi import Request
from fastapi.responses import JSONResponse


async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions with a 400 response."""
    return JSONResponse(
        status_code=400,
        content={"error": str(exc), "detail": "Invalid input provided."},
    )


async def generic_error_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions with a 500 response."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again.",
        },
    )
