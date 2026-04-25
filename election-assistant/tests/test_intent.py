from app.services.intent_service import IntentService

def test_keyword_classification():
    service = IntentService()
    # Assume we don't have API key for these simple unit tests, thus triggering fallback
    intent = service._keyword_classify("How do I register to vote?")
    assert intent == "registration"
    
    intent = service._keyword_classify("When is the deadline to vote by mail?")
    assert intent == "deadlines"
    
    intent = service._keyword_classify("Where is my polling location?")
    assert intent == "polling_locations"

def test_suggestions():
    service = IntentService()
    suggestions = service.get_follow_up_suggestions("registration")
    assert len(suggestions) > 0
    assert "deadline" in str(suggestions).lower()
