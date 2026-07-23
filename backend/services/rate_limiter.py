import logging
from dataclasses import dataclass

from core.config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS
from services.redis import redisservices

logger = logging.getLogger(__name__)

# Atomic fixed-window counter: INCR the key, and set its TTL only on the first
# hit of the window. Running it as a single Lua script avoids the race where a
# key is incremented but never expires (which would lock a client out forever).
_FIXED_WINDOW_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""


@dataclass
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after: int


class RateLimiter:
    """Redis-backed fixed-window rate limiter."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds

    async def check(self, identity: str) -> RateLimitResult:
        """Count one request against ``identity`` and report whether it's allowed.

        Fails open: if Redis is unavailable the request is allowed so an outage
        in the limiter never takes down the API.
        """
        redis = redisservices.redis
        if redis is None:
            logger.warning("Rate limiter: Redis not connected, allowing request")
            return RateLimitResult(True, self.limit, self.limit, 0)

        key = f"ratelimit:{identity}"
        try:
            current = await redis.eval(
                _FIXED_WINDOW_SCRIPT, 1, key, self.window_seconds
            )
            current = int(current)
        except Exception as exc:  # network hiccup, script error, etc.
            logger.error(f"Rate limiter check failed, allowing request: {exc}")
            return RateLimitResult(True, self.limit, self.limit, 0)

        if current > self.limit:
            # Key already exists; ask Redis how long until the window resets.
            try:
                ttl = await redis.ttl(key)
            except Exception:
                ttl = self.window_seconds
            retry_after = ttl if ttl and ttl > 0 else self.window_seconds
            return RateLimitResult(False, self.limit, 0, retry_after)

        return RateLimitResult(
            allowed=True,
            limit=self.limit,
            remaining=max(self.limit - current, 0),
            retry_after=0,
        )


rate_limiter = RateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)
