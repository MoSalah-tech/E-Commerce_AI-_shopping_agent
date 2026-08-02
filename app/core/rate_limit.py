import time
from collections import defaultdict
from typing import Dict, List

from fastapi import Request, HTTPException, status

from app.core.config import RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS

# NOTE: in-memory only — resets on server restart, and does NOT share state
# across multiple server instances/processes. Fine for local dev and a
# single-instance deployment. Swap for a Redis-backed limiter if you ever
# run more than one instance behind a load balancer.


def make_rate_limiter(max_requests: int, window_seconds: int):
    """Factory so different routes can have different limits, each with its own log."""
    request_log: Dict[str, List[float]] = defaultdict(list)

    async def limiter(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - window_seconds

        recent = [t for t in request_log[client_ip] if t > window_start]

        if len(recent) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: max {max_requests} requests per {window_seconds}s.",
            )

        recent.append(now)
        request_log[client_ip] = recent

    return limiter


# Existing chat rate limit — unchanged behavior
rate_limit = make_rate_limiter(RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)

# Stricter limiter for auth endpoints — tune these numbers to taste
auth_rate_limit = make_rate_limiter(max_requests=5, window_seconds=60)