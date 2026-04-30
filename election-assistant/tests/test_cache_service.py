"""Tests for Cache Service - Redis caching"""

import pytest
from unittest.mock import patch, Mock, MagicMock
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock redis module to avoid import errors
sys.modules['redis'] = MagicMock()

from app.services.cache_service import CacheService


class TestCacheService:
    """Test suite for Cache Service"""

    # ==================== get tests ====================

    @patch('app.services.cache_service.config')
    def test_get_success(self, mock_config):
        """Test get retrieves cached value successfully"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            test_data = {"key": "value", "count": 42}
            mock_redis.get.return_value = json.dumps(test_data)

            service = CacheService()
            result = service.get("test:key")

            mock_redis.get.assert_called_once_with("test:key")
            assert result == test_data

    @patch('app.services.cache_service.config')
    def test_get_missing_key(self, mock_config):
        """Test get returns None for missing key"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.get.return_value = None

            service = CacheService()
            result = service.get("nonexistent:key")

            assert result is None

    @patch('app.services.cache_service.config')
    def test_get_disabled_cache(self, mock_config):
        """Test get returns None when Redis cache is disabled"""
        mock_config.ENABLE_REDIS_CACHE = False

        service = CacheService()
        result = service.get("any:key")

        assert result is None

    @patch('app.services.cache_service.config')
    def test_get_exception_returns_none(self, mock_config):
        """Test get returns None on Redis exception"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.get.side_effect = Exception("Redis connection error")

            service = CacheService()
            result = service.get("test:key")

            assert result is None

    @patch('app.services.cache_service.config')
    def test_get_invalid_json(self, mock_config):
        """Test get returns None when cached value is invalid JSON"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.get.return_value = "not valid json{"

            service = CacheService()
            result = service.get("test:key")

            assert result is None

    # ==================== set tests ====================

    @patch('app.services.cache_service.config')
    def test_set_success(self, mock_config):
        """Test set stores value in cache successfully"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.setex.return_value = True

            service = CacheService()
            test_value = {"status": "active", "data": [1, 2, 3]}
            result = service.set("test:key", test_value, ttl=3600)

            mock_redis.setex.assert_called_once_with("test:key", 3600, json.dumps(test_value))
            assert result is True

    @patch('app.services.cache_service.config')
    def test_set_default_ttl(self, mock_config):
        """Test set uses default TTL when not specified"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.setex.return_value = True

            service = CacheService()
            result = service.set("test:key", {"data": "value"})

            call_args = mock_redis.setex.call_args
            assert call_args[0][1] == 3600  # Default CACHE_TTL_MEDIUM

    @patch('app.services.cache_service.config')
    def test_set_disabled_cache(self, mock_config):
        """Test set returns False when Redis cache is disabled"""
        mock_config.ENABLE_REDIS_CACHE = False

        service = CacheService()
        result = service.set("test:key", {"data": "value"})

        assert result is False

    @patch('app.services.cache_service.config')
    def test_set_exception_returns_false(self, mock_config):
        """Test set returns False on Redis exception"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.setex.side_effect = Exception("Redis write error")

            service = CacheService()
            result = service.set("test:key", {"data": "value"})

            assert result is False

    # ==================== delete tests ====================

    @patch('app.services.cache_service.config')
    def test_delete_success(self, mock_config):
        """Test delete removes key from cache successfully"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.delete.return_value = 1

            service = CacheService()
            result = service.delete("test:key")

            mock_redis.delete.assert_called_once_with("test:key")
            assert result is True

    @patch('app.services.cache_service.config')
    def test_delete_nonexistent_key(self, mock_config):
        """Test delete handles nonexistent key gracefully"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.delete.return_value = 0

            service = CacheService()
            result = service.delete("nonexistent:key")

            assert result is True  # Still returns True even if key didn't exist

    @patch('app.services.cache_service.config')
    def test_delete_disabled_cache(self, mock_config):
        """Test delete returns False when Redis cache is disabled"""
        mock_config.ENABLE_REDIS_CACHE = False

        service = CacheService()
        result = service.delete("test:key")

        assert result is False

    @patch('app.services.cache_service.config')
    def test_delete_exception_returns_false(self, mock_config):
        """Test delete returns False on Redis exception"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.delete.side_effect = Exception("Redis delete error")

            service = CacheService()
            result = service.delete("test:key")

            assert result is False

    # ==================== get_session tests ====================

    @patch('app.services.cache_service.config')
    def test_get_session_success(self, mock_config):
        """Test get_session retrieves session data"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            session_data = {"user_id": "123", "authenticated": True, "preferences": {"lang": "en"}}
            mock_redis.get.return_value = json.dumps(session_data)

            service = CacheService()
            result = service.get_session("session_abc123")

            expected_key = f"session:session_abc123"
            mock_redis.get.assert_called_once_with(expected_key)
            assert result == session_data

    @patch('app.services.cache_service.config')
    def test_get_session_missing(self, mock_config):
        """Test get_session returns None when session not found"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.get.return_value = None

            service = CacheService()
            result = service.get_session("session_nonexistent")

            assert result is None

    @patch('app.services.cache_service.config')
    def test_get_session_disabled_cache(self, mock_config):
        """Test get_session returns None when cache disabled"""
        mock_config.ENABLE_REDIS_CACHE = False

        service = CacheService()
        result = service.get_session("session_any")

        assert result is None

    # ==================== set_session tests ====================

    @patch('app.services.cache_service.config')
    def test_set_session_success(self, mock_config):
        """Test set_session stores session data with long TTL"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.setex.return_value = True

            service = CacheService()
            session_data = {"user_id": "123", "authenticated": True}
            result = service.set_session("session_abc123", session_data)

            assert result is True
            call_args = mock_redis.setex.call_args[0]
            assert call_args[0] == "session:session_abc123"
            assert call_args[1] == 86400  # CACHE_TTL_LONG
            parsed_value = json.loads(call_args[2])
            assert parsed_value == session_data

    @patch('app.services.cache_service.config')
    def test_set_session_disabled_cache(self, mock_config):
        """Test set_session returns False when cache disabled"""
        mock_config.ENABLE_REDIS_CACHE = False

        service = CacheService()
        result = service.set_session("session_any", {"data": "value"})

        assert result is False

    @patch('app.services.cache_service.config')
    def test_set_session_exception_returns_false(self, mock_config):
        """Test set_session returns False on Redis exception"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.setex.side_effect = Exception("Redis write error")

            service = CacheService()
            result = service.set_session("session_abc", {"data": "value"})

            assert result is False

    # ==================== health_check tests ====================

    @patch('app.services.cache_service.config')
    def test_health_check_success(self, mock_config):
        """Test health_check returns True when Redis is available"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.ping.return_value = True

            service = CacheService()
            result = service.health_check()

            mock_redis.ping.assert_called_once()
            assert result is True

    @patch('app.services.cache_service.config')
    def test_health_check_redis_unavailable(self, mock_config):
        """Test health_check returns False when Redis ping fails"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.ping.side_effect = Exception("Redis down")

            service = CacheService()
            result = service.health_check()

            assert result is False

    @patch('app.services.cache_service.config')
    def test_health_check_disabled_cache(self, mock_config):
        """Test health_check returns False when cache is disabled"""
        mock_config.ENABLE_REDIS_CACHE = False

        service = CacheService()
        result = service.health_check()

        assert result is False

    # ==================== Existing tests (kept and enhanced) ====================

    @patch('app.services.cache_service.config')
    def test_clear_pattern_test(self, mock_config):
        """Test clear_pattern removes cache entries matching a pattern"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.keys.return_value = [b"user:123", b"user:456"]
            mock_redis.delete.return_value = 2

            service = CacheService()
            result = service.clear_pattern("user:*")

            # Verify pattern matching and deletion happened
            mock_redis.keys.assert_called_with("user:*")
            mock_redis.delete.assert_called_with(b"user:123", b"user:456")
            assert result == 2

    @patch('app.services.cache_service.config')
    def test_get_intent_result_test(self, mock_config):
        """Test get_intent_result retrieves cached intent data"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            # Mock cached data
            cached_data = json.dumps({
                "intent": "question",
                "confidence": 0.88
            })
            mock_redis.get.return_value = cached_data

            service = CacheService()
            result = service.get_intent_result("test_message_key")

            # Verify redis.get was called
            mock_redis.get.assert_called_once()
            assert result is not None
            assert isinstance(result, dict)
            assert result["intent"] == "question"

    @patch('app.services.cache_service.config')
    def test_set_intent_result_test(self, mock_config):
        """Test set_intent_result stores intent in cache"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.setex.return_value = True

            service = CacheService()
            result = service.set_intent_result("user_123", "greeting", 0.95)

            # Verify setex was called with TTL and data
            mock_redis.setex.assert_called_once()
            assert result is True

    @patch('app.services.cache_service.config')
    def test_get_timeline_test(self, mock_config):
        """Test get_timeline retrieves cached timeline data"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            cached_timeline = json.dumps([
                {"event": "login", "time": "10:00"},
                {"event": "search", "time": "10:05"}
            ])
            mock_redis.get.return_value = cached_timeline

            service = CacheService()
            result = service.get_timeline()

            mock_redis.get.assert_called_once()
            assert result is not None
            assert isinstance(result, list)

    @patch('app.services.cache_service.config')
    def test_set_timeline_test(self, mock_config):
        """Test set_timeline stores timeline in cache"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.setex.return_value = True

            service = CacheService()
            timeline_data = [
                {"event": "login", "timestamp": "2024-01-01T10:00:00"},
                {"event": "logout", "timestamp": "2024-01-01T18:00:00"}
            ]
            result = service.set_timeline(timeline_data)

            mock_redis.setex.assert_called_once()
            assert result is True

    # ==================== Edge case and boundary tests ====================

    @patch('app.services.cache_service.config')
    def test_get_empty_string_value(self, mock_config):
        """Test get handles empty string from Redis"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.get.return_value = ""

            service = CacheService()
            result = service.get("test:key")

            assert result is None

    @patch('app.services.cache_service.config')
    def test_set_empty_value(self, mock_config):
        """Test set handles empty dict/value correctly"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.setex.return_value = True

            service = CacheService()
            result = service.set("test:key", {})

            assert result is True
            call_args = mock_redis.setex.call_args[0]
            assert call_args[2] == "{}"

    @patch('app.services.cache_service.config')
    def test_set_zero_ttl(self, mock_config):
        """Test set with TTL=0 (edge case)"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.setex.return_value = True

            service = CacheService()
            result = service.set("test:key", "value", ttl=0)

            assert result is True
            call_args = mock_redis.setex.call_args[0]
            assert call_args[1] == 0

    @patch('app.services.cache_service.config')
    def test_set_negative_ttl(self, mock_config):
        """Test set with negative TTL (should still attempt to set)"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.setex.return_value = True

            service = CacheService()
            result = service.set("test:key", "value", ttl=-1)

            assert result is True
            call_args = mock_redis.setex.call_args[0]
            assert call_args[1] == -1

    @patch('app.services.cache_service.config')
    def test_clear_pattern_empty_result(self, mock_config):
        """Test clear_pattern with no matching keys"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.keys.return_value = []

            service = CacheService()
            result = service.clear_pattern("nonexistent:*")

            assert result == 0
            mock_redis.delete.assert_not_called()

    @patch('app.services.cache_service.config')
    def test_clear_pattern_disabled_cache(self, mock_config):
        """Test clear_pattern returns 0 when cache disabled"""
        mock_config.ENABLE_REDIS_CACHE = False

        service = CacheService()
        result = service.clear_pattern("any:pattern")

        assert result == 0

    @patch('app.services.cache_service.config')
    def test_clear_pattern_exception(self, mock_config):
        """Test clear_pattern returns 0 on exception"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.keys.side_effect = Exception("Redis error")

            service = CacheService()
            result = service.clear_pattern("test:*")

            assert result == 0

    @patch('app.services.cache_service.config')
    def test_get_intent_result_with_none(self, mock_config):
        """Test get_intent_result returns None for missing data"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.get.return_value = None

            service = CacheService()
            result = service.get_intent_result("hash123")

            assert result is None

    @patch('app.services.cache_service.config')
    def test_set_intent_result_with_low_confidence(self, mock_config):
        """Test set_intent_result with boundary confidence value 0.0"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.setex.return_value = True

            service = CacheService()
            result = service.set_intent_result("hash123", "unknown", 0.0)

            assert result is True
            call_args = mock_redis.setex.call_args[0]
            parsed_value = json.loads(call_args[2])
            assert parsed_value["confidence"] == 0.0

    @patch('app.services.cache_service.config')
    def test_set_intent_result_with_max_confidence(self, mock_config):
        """Test set_intent_result with boundary confidence value 1.0"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.setex.return_value = True

            service = CacheService()
            result = service.set_intent_result("hash123", "certain", 1.0)

            assert result is True
            call_args = mock_redis.setex.call_args[0]
            parsed_value = json.loads(call_args[2])
            assert parsed_value["confidence"] == 1.0

    @patch('app.services.cache_service.config')
    def test_get_timeline_empty_list(self, mock_config):
        """Test get_timeline with empty list cache"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.get.return_value = "[]"

            service = CacheService()
            result = service.get_timeline()

            assert result == []

    @patch('app.services.cache_service.config')
    def test_set_timeline_empty_dict(self, mock_config):
        """Test set_timeline with empty dict"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.setex.return_value = True

            service = CacheService()
            result = service.set_timeline({})

            assert result is True
            call_args = mock_redis.setex.call_args[0]
            assert call_args[2] == "{}"

    @patch('app.services.cache_service.config')
    def test_get_intent_result_invalid_json(self, mock_config):
        """Test get_intent_result handles invalid JSON gracefully"""
        mock_config.ENABLE_REDIS_CACHE = True
        mock_config.REDIS_HOST = "localhost"
        mock_config.REDIS_PORT = 6379
        mock_config.REDIS_PASSWORD = None

        with patch('redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            mock_redis.get.return_value = "{malformed json"

            service = CacheService()
            result = service.get_intent_result("hash123")

            assert result is None
