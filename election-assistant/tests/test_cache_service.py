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