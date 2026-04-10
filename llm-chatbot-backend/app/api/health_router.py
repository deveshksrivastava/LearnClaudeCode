# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This file defines the GET /api/v1/health endpoint.
# A health endpoint is used by Azure Container Apps, Kubernetes, and load
# balancers to check if the service is running. If this returns a non-200
# response, the infrastructure automatically restarts the container.
# ─────────────────────────────────────────────────────────────────────────────

from fastapi import APIRouter, Depends
from app.models import HealthResponse
from app.config import Settings, get_settings

# APIRouter groups related endpoints together.
# The prefix and tags are applied to all routes defined in this router.
router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns service health status. Used by load balancers and container orchestrators.",
)
def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """
    Health check endpoint — GET /api/v1/health.

    WHAT DOES THIS DO?
      Returns a simple JSON response indicating the service is alive.
      This must be fast (no DB calls, no LLM calls).

    WHY Depends(get_settings)?
      FastAPI's Depends() is dependency injection — it calls get_settings()
      and passes the result as the 'settings' parameter.
      This is how we avoid global variables while still sharing objects.

    Args:
        settings: Application settings (injected by FastAPI).

    Returns:
        HealthResponse: JSON response with status and version.
    """
    return HealthResponse(
        status="ok",
        version=settings.app_version,
    )
