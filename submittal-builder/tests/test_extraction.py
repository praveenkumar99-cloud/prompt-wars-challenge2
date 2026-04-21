import pytest
from app.services.extraction_service import ExtractionService

def test_regex_extract():
    service = ExtractionService()
    text = "Here is a BOM with part PWR-4000-XL and CTL-MOD-128."
    parts = service._regex_extract(text)
    assert "PWR-4000-XL" in parts
    assert "CTL-MOD-128" in parts

def test_normalization():
    service = ExtractionService()
    parts = [" pwr-4000-XL ", "CTL-mod-128 "]
    normalized = service._normalize(parts)
    assert "PWR-4000-XL" in normalized
    assert "CTL-MOD-128" in normalized
