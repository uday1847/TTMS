from typing import Any
import time

class PermissionCacheService:
    """
    In-memory cache for RBAC permissions.
    In a real enterprise environment, this would use Redis.
    """
    _cache: dict[str, tuple[Any, float]] = {}
    _ttl_seconds = 300  # 5 minutes

    @classmethod
    def get(cls, key: str) -> Any | None:
        if key in cls._cache:
            value, expiry = cls._cache[key]
            if time.time() < expiry:
                return value
            else:
                del cls._cache[key]
        return None

    @classmethod
    def set(cls, key: str, value: Any, ttl: int | None = None) -> None:
        expiry = time.time() + (ttl or cls._ttl_seconds)
        cls._cache[key] = (value, expiry)

    @classmethod
    def invalidate(cls, key: str) -> None:
        if key in cls._cache:
            del cls._cache[key]

    @classmethod
    def invalidate_user_permissions(cls, user_id: str) -> None:
        cls.invalidate(f"user_permissions:{user_id}")

    @classmethod
    def invalidate_all_permissions(cls) -> None:
        # Invalidate all user permissions by clearing the whole cache for simplicity
        cls._cache.clear()
