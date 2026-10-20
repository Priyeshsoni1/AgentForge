
import hmac
import json
import time
from collections import defaultdict, deque
from collections.abc import Callable

from fastapi import Depends, Header, HTTPException, Request

from agentforge.core.config import settings


def get_api_key_owners() -> dict[str, str]:
    """Return owner_id -> API key mapping from configuration."""
    raw = settings.app_api_keys

    if not raw:
        return {}

    try:
        parsed = json.loads(raw.get_secret_value())
    except json.JSONDecodeError as exc:
        raise RuntimeError("APP_API_KEYS must contain valid JSON.") from exc

    if not isinstance(parsed, dict):
        raise RuntimeError("APP_API_KEYS must be a JSON object.")

    if not all(
        isinstance(owner, str)
        and owner
        and isinstance(key, str)
        and len(key) >= 32
        for owner, key in parsed.items()
    ):
        raise RuntimeError(
            "Each API key must be a string of at least 32 characters."
        )

    return parsed


async def get_current_owner(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> str:
    owners = get_api_key_owners()

    if not owners:
        raise HTTPException(
            status_code=503,
            detail="API authentication is not configured.",
        )

    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key.",
        )

    for owner_id, configured_key in owners.items():
        if hmac.compare_digest(x_api_key, configured_key):
            return owner_id

    raise HTTPException(
        status_code=401,
        detail="Invalid API key.",
    )


class InMemoryRateLimiter:
    """Sliding-window rate limiter for local development and tests."""

    def __init__(self, limit: int, window_seconds: int):
        from collections import defaultdict, deque
        import asyncio

        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def check(self, owner_id: str) -> bool:
        import time

        now = time.monotonic()
        cutoff = now - self.window_seconds

        async with self._lock:
            timestamps = self.requests[owner_id]

            # Remove requests outside the sliding time window.
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            # Reject requests after reaching the limit.
            if len(timestamps) >= self.limit:
                return False

            timestamps.append(now)
            return True

class RedisRateLimiter:
    """Shared sliding-window rate limiter using Redis."""

    def __init__(self, redis_client, limit: int, window_seconds: int):
        self.redis = redis_client
        self.limit = limit
        self.window_seconds = window_seconds

    async def check(self, owner_id: str) -> bool:
        now = time.time()
        key = f"agentforge:rate:{owner_id}"
        cutoff = now - self.window_seconds
        member = f"{now}:{time.time_ns()}"

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, "-inf", cutoff)
            pipe.zcard(key)
            results = await pipe.execute()

            count = results[1]

            if count >= self.limit:
                return False

            async with self.redis.pipeline(transaction=True) as write:
                write.zadd(key, {member: now})
                write.expire(key, self.window_seconds + 1)
                await write.execute()

        return True


async def enforce_rate_limit(
    request: Request,
    owner_id: str = Depends(get_current_owner),
) -> None:
    limiter = getattr(request.app.state, "rate_limiter", None)

    if limiter is None:
        raise HTTPException(
            status_code=503,
            detail="Rate limiter is unavailable.",
        )

    try:
        allowed = await limiter.check(owner_id)
    except Exception as exc:
        # Fail closed: don't serve protected requests when a shared
        # production limiter fails.
        if settings.environment.lower() != "development":
            raise HTTPException(
                status_code=503,
                detail="Rate limiter is temporarily unavailable.",
            ) from exc

        raise HTTPException(
            status_code=503,
            detail="Rate limiter is unavailable.",
        ) from exc

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later.",
            headers={"Retry-After": str(settings.rate_limit_window_seconds)},
        )

