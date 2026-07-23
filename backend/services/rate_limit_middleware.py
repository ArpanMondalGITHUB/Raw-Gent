import hashlib
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from core.config import COOKIE_ACCESS_NAME
from services.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

# Paths that should never be rate limited (health checks, etc.).
EXEMPT_PATHS = {"/health"}


def _client_identity(request: Request) -> str:
    """Identify the caller: prefer the authenticated session, fall back to IP.

    The access-token cookie is hashed so we never use a raw credential as a
    Redis key.
    """
    token = request.cookies.get(COOKIE_ACCESS_NAME)
    if token:
        digest = hashlib.sha256(token.encode()).hexdigest()[:32]
        return f"user:{digest}"

    # Respect a proxy's forwarded IP if present, else the direct peer.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Reject callers that exceed the configured request budget with a 429.

    Only HTTP requests pass through ``BaseHTTPMiddleware``; WebSocket
    connections bypass it entirely, so the ``/ws/...` routes are unaffected.
    """

    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        identity = _client_identity(request)
        result = await rate_limiter.check(identity)

        if not result.allowed:
            logger.warning(f"Rate limit exceeded for {identity} on {request.url.path}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={
                    "Retry-After": str(result.retry_after),
                    "X-RateLimit-Limit": str(result.limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)
        return response
