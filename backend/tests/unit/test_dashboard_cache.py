import pytest
import time
from app.application.services.dashboard_cache_service import DashboardCacheService

def test_cache_set_and_get():
    DashboardCacheService.clear()
    DashboardCacheService.set("dashboard:test", {"hello": "world"})
    
    result = DashboardCacheService.get("dashboard:test")
    assert result == {"hello": "world"}

def test_cache_expiration():
    DashboardCacheService.clear()
    DashboardCacheService.set("financial:temp", 100, ttl=1)
    
    assert DashboardCacheService.get("financial:temp") == 100
    time.sleep(1.1)
    # Should expire
    assert DashboardCacheService.get("financial:temp") is None

def test_cache_invalidation():
    DashboardCacheService.clear()
    DashboardCacheService.set("dashboard:1", "data1")
    DashboardCacheService.set("dashboard:2", "data2")
    DashboardCacheService.set("fuel:1", "data3")
    
    DashboardCacheService.invalidate_dashboard()
    
    assert DashboardCacheService.get("dashboard:1") is None
    assert DashboardCacheService.get("dashboard:2") is None
    assert DashboardCacheService.get("fuel:1") == "data3"
