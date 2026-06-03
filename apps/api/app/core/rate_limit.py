import time
import uuid
from fastapi import HTTPException, Request, status
from app.core.redis import get_redis_client
from app.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    async def check_rate_limit(self, key: str, limit: int, window_seconds: int) -> None:
        """Enforces a sliding window rate limit using Redis sorted sets.

        Args:
            key: Redis key for rate limiting bucket
            limit: Maximum requests allowed in the window
            window_seconds: Size of sliding window in seconds

        Raises:
            HTTPException with status 429 and Retry-After header if limit exceeded.
        """
        redis_client = get_redis_client()
        now = time.time()
        cutoff = now - window_seconds

        # Wrap in pipeline for atomic checks
        async with redis_client.pipeline(transaction=True) as pipe:
            # Clean up old requests outside the sliding window
            pipe.zremrangebyscore(key, 0, cutoff)
            # Count the remaining requests in the window
            pipe.zcard(key)
            # Get the oldest timestamp in the current window to compute Retry-After
            pipe.zrange(key, 0, 0, withscores=True)

            results = await pipe.execute()
            _, count, oldest_entries = results

        if count >= limit:
            if oldest_entries:
                # oldest_entries format: [(member, score)]
                # depending on decode_responses, score is a float or oldest_entries[0] has (member, score)
                oldest_score = oldest_entries[0][1]
                retry_after = int(oldest_score + window_seconds - now)
            else:
                retry_after = window_seconds

            retry_after = max(1, retry_after)

            logger.warning(
                "rate_limit_exceeded",
                key=key,
                count=count,
                limit=limit,
                retry_after=retry_after,
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": str(retry_after)},
            )

        # Record this request
        async with redis_client.pipeline(transaction=True) as pipe:
            # Member must be unique to prevent overwriting scores for simultaneous requests
            member = f"{now}:{uuid.uuid4().hex}"
            pipe.zadd(key, {member: now})
            pipe.expire(key, window_seconds * 2)
            await pipe.execute()


rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "127.0.0.1"
