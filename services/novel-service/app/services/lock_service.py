import asyncio
import time
from typing import Optional

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

from app.core.config import settings


_lock_store: dict[str, dict] = {}


class LockService:
    def __init__(self):
        self._redis = None
        if redis and settings.redis_url and settings.app_env == "production":
            try:
                self._redis = redis.from_url(settings.redis_url)
            except Exception:
                self._redis = None

    async def acquire_lock(
        self,
        resource: str,
        holder: str,
        lock_type: str = "write",
        timeout: int = 1800,
    ) -> bool:
        if self._redis:
            key = f"lock:{resource}:{lock_type}"
            acquired = await self._redis.set(
                key, holder, ex=timeout, nx=True
            )
            return acquired is not None
        else:
            now = time.time()
            if resource in _lock_store:
                lock_info = _lock_store[resource]
                if lock_info["expires_at"] > now and lock_info["holder"] != holder:
                    return False
            _lock_store[resource] = {
                "holder": holder,
                "lock_type": lock_type,
                "acquired_at": now,
                "expires_at": now + timeout,
            }
            return True

    async def release_lock(self, resource: str, holder: str) -> bool:
        if self._redis:
            key = f"lock:{resource}:write"
            current = await self._redis.get(key)
            if current and current.decode() == holder:
                await self._redis.delete(key)
                return True
            return False
        else:
            if resource in _lock_store and _lock_store[resource]["holder"] == holder:
                del _lock_store[resource]
                return True
            return False

    async def get_lock_status(self, resource: str) -> dict:
        if self._redis:
            key = f"lock:{resource}:write"
            holder = await self._redis.get(key)
            ttl = await self._redis.ttl(key)
            return {
                "resource": resource,
                "locked": holder is not None,
                "holder": holder.decode() if holder else None,
                "expires_at": None,
            }
        else:
            now = time.time()
            if resource in _lock_store:
                lock_info = _lock_store[resource]
                if lock_info["expires_at"] > now:
                    return {
                        "resource": resource,
                        "locked": True,
                        "holder": lock_info["holder"],
                        "acquired_at": lock_info["acquired_at"],
                        "expires_at": lock_info["expires_at"],
                    }
                else:
                    del _lock_store[resource]
            return {
                "resource": resource,
                "locked": False,
                "holder": None,
                "acquired_at": None,
                "expires_at": None,
            }


lock_service = LockService()
