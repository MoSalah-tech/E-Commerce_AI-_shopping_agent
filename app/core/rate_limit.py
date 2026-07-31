import time
from collections import defaultdict
from typing import Dict, List

from fastapi import Request, HTTPException, status

from app.core.config import RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS

# NOTE: in-memory only — resets on server restart, and does NOT share state
# across multiple server instances/processes. Fine for local dev and a
# single-instance deployment. Swap for a Redis-backed limiter if you ever
# run more than one instance behind a load balancer.
_request_log: Dict[str, List[float]] = defaultdict(list)


async def rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    # Drop timestamps outside the current window, then check the count
    recent = [t for t in _request_log[client_ip] if t > window_start]

    if len(recent) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: max {RATE_LIMIT_MAX_REQUESTS} requests per {RATE_LIMIT_WINDOW_SECONDS}s.",
        )

    recent.append(now)
    _request_log[client_ip] = recent
