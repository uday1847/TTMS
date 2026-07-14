import time
from typing import Any, Optional, Dict


class DashboardCacheService:
    """
    In-memory cache implementation designed to easily transition to Redis in the future.
    """
    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        if key in cls._cache:
            entry = cls._cache[key]
            if entry["expires_at"] is None or entry["expires_at"] > time.time():
                return entry["value"]
            else:
                # Expired
                cls.delete(key)
        return None

    @classmethod
    def set(cls, key: str, value: Any, ttl: Optional[int] = 300) -> None:
        """Set a value with TTL in seconds (default 5 mins)"""
        expires_at = time.time() + ttl if ttl else None
        cls._cache[key] = {
            "value": value,
            "expires_at": expires_at
        }

    @classmethod
    def delete(cls, key: str) -> None:
        if key in cls._cache:
            del cls._cache[key]

    @classmethod
    def clear(cls) -> None:
        cls._cache.clear()

    @classmethod
    def invalidate_prefix(cls, prefix: str) -> None:
        keys_to_delete = [k for k in cls._cache.keys() if k.startswith(prefix)]
        for k in keys_to_delete:
            cls.delete(k)

    @classmethod
    def invalidate_dashboard(cls) -> None:
        cls.invalidate_prefix("dashboard:")

    @classmethod
    def invalidate_financial(cls) -> None:
        cls.invalidate_prefix("financial:")

    @classmethod
    def invalidate_fleet(cls) -> None:
        cls.invalidate_prefix("fleet:")

    @classmethod
    def invalidate_fuel(cls) -> None:
        cls.invalidate_prefix("fuel:")

    @classmethod
    def invalidate_maintenance(cls) -> None:
        cls.invalidate_prefix("maintenance:")
