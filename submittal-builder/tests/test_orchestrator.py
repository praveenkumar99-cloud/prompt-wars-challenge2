import pytest
from unittest.mock import MagicMock
from app.services.orchestrator import Orchestrator

def test_orchestrator_initializes():
    orchestrator = Orchestrator()
    assert orchestrator.extraction_service is not None
    assert orchestrator.retrieval_service is not None
    assert orchestrator.assembly_service is not None
