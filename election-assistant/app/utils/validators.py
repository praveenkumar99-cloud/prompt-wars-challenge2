"""Validation functionality"""
def is_valid_input(text: str) -> bool:
    """Check text safety and length"""
    return len(text) > 2 and len(text) < 1000
