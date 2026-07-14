import time
import pytest
from app.application.services.permission_cache_service import PermissionCacheService

@pytest.fixture(autouse=True)
def clear_cache():
    PermissionCacheService.invalidate_all_permissions()
    yield
    PermissionCacheService.invalidate_all_permissions()

def test_cache_insert_and_lookup():
    PermissionCacheService.set("test_key", "test_value")
    assert PermissionCacheService.get("test_key") == "test_value"

def test_cache_lookup_missing():
    assert PermissionCacheService.get("missing_key") is None

def test_cache_expiration():
    PermissionCacheService.set("test_key", "test_value", ttl=1)
    assert PermissionCacheService.get("test_key") == "test_value"
    time.sleep(1.1)
    assert PermissionCacheService.get("test_key") is None

def test_cache_invalidation():
    PermissionCacheService.set("test_key", "test_value")
    PermissionCacheService.invalidate("test_key")
    assert PermissionCacheService.get("test_key") is None

def test_invalidate_user_permissions():
    user_id = "user123"
    key = f"user_permissions:{user_id}"
    PermissionCacheService.set(key, ["read", "write"])
    assert PermissionCacheService.get(key) == ["read", "write"]
    
    PermissionCacheService.invalidate_user_permissions(user_id)
    assert PermissionCacheService.get(key) is None

def test_invalidate_all_permissions():
    PermissionCacheService.set("user_permissions:user1", ["read"])
    PermissionCacheService.set("user_permissions:user2", ["write"])
    PermissionCacheService.set("other_key", "value")
    
    PermissionCacheService.invalidate_all_permissions()
    
    assert PermissionCacheService.get("user_permissions:user1") is None
    assert PermissionCacheService.get("user_permissions:user2") is None
    assert PermissionCacheService.get("other_key") is None
