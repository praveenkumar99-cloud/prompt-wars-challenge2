"""Main assistant orchestrating all services"""
import logging
from typing import Dict, List
from .gemini_service import GeminiService
from .intent_service import IntentService
from .timeline_service import TimelineService

logger = logging.getLogger(__name__)

class AssistantService:
    """Main election assistant orchestrator"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
        self.intent_service = IntentService()
        self.timeline_service = TimelineService()
    
    async def process_message(self, message: str, session_id: str = None) -> Dict:
        """Process user message and return assistant response"""
        logger.info(f"Processing message: {message[:50]}...")
        
        # Step 1: Classify intent
        intent, confidence = self.intent_service.classify(message)
        logger.info(f"Intent: {intent} (confidence: {confidence})")
        
        # Step 2: Get context for intent
        context = self._get_context_for_intent(intent)
        
        # Step 3: Generate response
        if self.gemini_service.api_key:
            response_text = self.gemini_service.generate_response(message, intent, context)
        else:
            response_text = self._get_template_response(intent, context)
        
        # Step 4: Get follow-up suggestions
        follow_ups = self.intent_service.get_follow_up_suggestions(intent)
        
        # Step 5: Get sources
        sources = self._get_sources(intent)
        
        return {
            "response": response_text,
            "intent": intent,
            "follow_up_suggestions": follow_ups[:3],
            "sources": sources
        }
    
    def _get_context_for_intent(self, intent: str) -> Dict:
        """Get relevant context based on intent"""
        context_map = {
            "registration": {
                "description": "Register to vote online, by mail, or in-person",
                "deadline": "Varies by state, typically 15-30 days before Election Day",
                "requirements": "US citizen, state resident, 18+ by Election Day"
            },
            "deadlines": {
                "events": self.timeline_service.get_upcoming_events(),
                "registration_deadline": "Varies by state",
                "election_day": "November 5, 2024"
            },
            "voting_methods": {
                "options": ["In-person early", "In-person Election Day", "Vote by mail", "Absentee ballot"],
                "note": "Availability varies by state"
            },
            "requirements": {
                "id_requirements": "Varies by state - some require photo ID, others accept non-photo ID",
                "eligibility": "US citizen, state resident, 18+ by Election Day"
            },
            "polling_locations": {
                "where_to_find": "Voter registration card or state election website",
                "typical_hours": "7 AM - 7 PM"
            },
            "candidates": {
                "where_to_find": "State election website for sample ballot"
            },
            "general": {
                "help_topics": ["Registration", "Deadlines", "Voting methods", "ID requirements", "Polling places"]
            }
        }
        return context_map.get(intent, context_map["general"])
    
    def _get_template_response(self, intent: str, context: Dict) -> str:
        """Template responses when Gemini is unavailable"""
        templates = {
            "registration": "To register to vote, you can register online, by mail, or in person. The deadline varies by state but is typically 15-30 days before Election Day. You'll need to be a US citizen, state resident, and at least 18 years old by Election Day.",
            "deadlines": f"Key upcoming election dates include: {', '.join([e.get('event', '') for e in context.get('events', [])])}. Election Day is November 5, 2024. Check your state for specific registration deadlines.",
            "voting_methods": "You have several voting options: in-person early voting, in-person on Election Day, voting by mail, or absentee ballot. Availability varies by state.",
            "requirements": "Voter ID requirements vary by state. Some states require a government-issued photo ID, while others accept non-photo ID like a utility bill. First-time voters may need additional documentation.",
            "polling_locations": "Find your polling place on your voter registration card or your state's election website. Polling places are typically open from 7 AM to 7 PM on Election Day.",
            "candidates": "To see candidates on your ballot, check your state's election website for a sample ballot. You can research candidates on Ballotpedia or Vote411.",
            "general": "I can help you with voter registration, election deadlines, voting methods, ID requirements, finding your polling place, and candidate information. What specific information do you need?"
        }
        return templates.get(intent, templates["general"])
    
    def _get_sources(self, intent: str) -> List[str]:
        """Get reliable sources for information"""
        return [
            "USA.gov Voting & Election Information",
            "National Conference of State Legislatures",
            "Your State Election Office Website"
        ]
