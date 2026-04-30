"""Tests for Vertex AI Service - GCP integration"""

import pytest
from unittest.mock import patch, Mock, MagicMock
import json
import sys

# Mock vertexai modules to avoid import errors
sys.modules['vertexai'] = MagicMock()
sys.modules['vertexai.generative_models'] = MagicMock()

from app.services.vertex_ai_service import VertexAIService


class TestVertexAIService:
    """Test suite for Vertex AI Service"""

    @patch('app.services.vertex_ai_service.config')
    @patch('vertexai.generative_models.GenerativeModel')
    def test_understand_intent_advanced_success(self, mock_model_class, mock_config):
        mock_config.ENABLE_VERTEX_AI = True
        mock_config.GCP_PROJECT_ID = "test-project"
        mock_config.VERTEX_AI_LOCATION = "us-west1"

        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '{"intent": "registration", "confidence": 0.85}'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        # Test
        service = VertexAIService()
        intent, confidence = service.understand_intent_advanced("How do I register to vote?")

        # Assertions
        assert intent == "registration"
        assert confidence == 0.85
        mock_model.generate_content.assert_called_once()

    @patch('app.services.vertex_ai_service.config')
    @patch('vertexai.generative_models.GenerativeModel')
    def test_understand_intent_advanced_empty_input(self, mock_model_class, mock_config):
        """Test understand_intent_advanced with empty input."""
        mock_config.ENABLE_VERTEX_AI = True
        mock_config.GCP_PROJECT_ID = "test-project"
        mock_config.VERTEX_AI_LOCATION = "us-west1"

        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '{"intent": "general", "confidence": 0.5}'
        mock_model.generate_content.return_value = mock_response

        mock_model_class.return_value = mock_model

        service = VertexAIService()
        intent, confidence = service.understand_intent_advanced("")

        assert intent == "general"
        assert confidence == 0.5

    @patch('app.services.vertex_ai_service.config')
    @patch('vertexai.generative_models.GenerativeModel')
    def test_understand_intent_advanced_api_failure(self, mock_model_class, mock_config):
        """Test understand_intent_advanced when API fails."""
        mock_config.ENABLE_VERTEX_AI = True
        mock_config.GCP_PROJECT_ID = "test-project"
        mock_config.VERTEX_AI_LOCATION = "us-west1"

        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API error")

        mock_model_class.return_value = mock_model

        service = VertexAIService()
        result = service.generate_follow_ups_advanced("registration")

        # Should return empty list
        assert result == []

    @patch('app.services.vertex_ai_service.config')
    @patch('vertexai.generative_models.GenerativeModel')
    def test_batch_process_messages_success(self, mock_model_class, mock_config):
        """Test batch_process_messages with successful responses."""
        mock_config.ENABLE_VERTEX_AI = True
        mock_config.GCP_PROJECT_ID = "test-project"
        mock_config.VERTEX_AI_LOCATION = "us-west1"

        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Visit your state's election website to register."
        mock_model.generate_content.return_value = mock_response

        mock_model_class.return_value = mock_model

        service = VertexAIService()
        messages = [
            {"text": "How do I register?", "intent": "registration", "context": {}},
            {"text": "What documents needed?", "intent": "requirements", "context": {}}
        ]
        result = service.batch_process_messages(messages)

        assert len(result) == 2
        assert result[0]["text"] == "How do I register?"
        assert result[0]["response"] == "Visit your state's election website to register."
        assert result[1]["text"] == "What documents needed?"
        assert result[1]["response"] == "Visit your state's election website to register."

    @patch('app.services.vertex_ai_service.config')
    @patch('vertexai.generative_models.GenerativeModel')
    def test_batch_process_messages_empty_list(self, mock_model_class, mock_config):
        """Test batch_process_messages with empty message list."""
        mock_config.ENABLE_VERTEX_AI = True
        mock_config.GCP_PROJECT_ID = "test-project"
        mock_config.VERTEX_AI_LOCATION = "us-west1"

        mock_model = Mock()
        mock_model_class.return_value = mock_model

        service = VertexAIService()
        result = service.batch_process_messages([])

        assert result == []

    @patch('app.services.vertex_ai_service.config')
    @patch('vertexai.generative_models.GenerativeModel')
    def test_batch_process_messages_api_failure(self, mock_model_class, mock_config):
        """Test batch_process_messages when API fails."""
        mock_config.ENABLE_VERTEX_AI = True
        mock_config.GCP_PROJECT_ID = "test-project"
        mock_config.VERTEX_AI_LOCATION = "us-west1"

        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API error")

        mock_model_class.return_value = mock_model

        service = VertexAIService()
        messages = [{"text": "How do I register?", "intent": "registration", "context": {}}]
        result = service.batch_process_messages(messages)

        # Should still return result with error response
        assert len(result) == 1
        assert "unable to generate" in result[0]["response"].lower()

    @patch('app.services.vertex_ai_service.config')
    def test_vertex_ai_disabled_fallback(self, mock_config):
        """Test fallback behavior when Vertex AI is disabled."""
        mock_config.ENABLE_VERTEX_AI = False

        service = VertexAIService()

        # Test understand_intent_advanced
        intent, confidence = service.understand_intent_advanced("test message")
        assert intent == "general"
        assert confidence == 0.5

        # Test generate_response_advanced
        result = service.generate_response_advanced("test", "general", {})
        assert "Unable to generate response" in result

        # Test generate_follow_ups_advanced
        result = service.generate_follow_ups_advanced("general")
        assert result == []

        # Test batch_process_messages
        result = service.batch_process_messages([{"text": "test"}])
        assert result == []

    @patch('app.services.vertex_ai_service.config')
    @patch('vertexai.init')
    def test_client_initialization_failure(self, mock_init, mock_config):
        """Test behavior when client initialization fails."""
        mock_config.ENABLE_VERTEX_AI = True
        mock_config.GCP_PROJECT_ID = "test-project"
        mock_config.VERTEX_AI_LOCATION = "us-west1"

        # Make vertexai.init raise an exception
        mock_init.side_effect = Exception("Init failed")

        service = VertexAIService()

        # Test that methods return fallback values
        intent, confidence = service.understand_intent_advanced("test")
        assert intent == "general"
        assert confidence == 0.5

        result = service.generate_response_advanced("test", "general", {})
        assert "Unable to generate response" in result

        result = service.generate_follow_ups_advanced("general")
        assert result == []

        result = service.batch_process_messages([{"text": "test"}])
        assert result == []