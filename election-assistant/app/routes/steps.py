"""Step-by-step guidance endpoints"""
from fastapi import APIRouter, HTTPException
from ..services.step_service import StepService

router = APIRouter(prefix="/api", tags=["steps"])
step_service = StepService()

@router.get("/steps")
async def get_all_steps():
    """Get all step-by-step guides"""
    steps = step_service.get_all_steps()
    return [step.dict() for step in steps]

@router.get("/steps/{step_id}")
async def get_step(step_id: str):
    """Get specific step-by-step guide"""
    steps_map = {
        "register": step_service.get_registration_steps(),
        "vote": step_service.get_voting_steps(),
        "mail_ballot": step_service.get_vote_by_mail_steps()
    }
    
    if step_id not in steps_map:
        raise HTTPException(404, f"Step {step_id} not found")
    
    return steps_map[step_id].dict()
