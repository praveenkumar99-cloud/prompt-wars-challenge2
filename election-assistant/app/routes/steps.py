"""Module: steps.py
Description: Step-by-step guidance endpoints.
Author: Praveen Kumar
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..constants import (
    STEP_ID_MAIL_BALLOT,
    STEP_ID_REGISTER,
    STEP_ID_VOTE,
)
from ..models import ElectionStep
from ..services.step_service import StepService

router = APIRouter(prefix="/api", tags=["steps"])


def get_step_service() -> StepService:
    """Dependency injection provider for StepService.

    Returns:
        StepService instance.
    """
    return StepService()


@router.get(
    "/steps",
    response_model=List[ElectionStep],
    status_code=200,
    tags=["steps"],
    summary="Get all step-by-step voting guides",
)
async def get_all_steps(
    service: StepService = Depends(get_step_service),
) -> List[ElectionStep]:
    """Get all available step-by-step guides.

    Returns:
        List of all ElectionStep objects covering registration, voting, and mail ballots.
    """
    return service.get_all_steps()


@router.get(
    "/steps/{step_id}",
    response_model=ElectionStep,
    status_code=200,
    tags=["steps"],
    summary="Get a specific step-by-step guide",
)
async def get_step(
    step_id: str, service: StepService = Depends(get_step_service)
) -> ElectionStep:
    """Get a specific step-by-step guide by ID.

    **Path Parameters:**
        - step_id: One of "register", "vote", or "mail_ballot"

    **Returns:**
        ElectionStep object with detailed guidance.

    **Error Responses:**
        - 404: Step ID not found
    """
    steps_map = {
        STEP_ID_REGISTER: service.get_registration_steps(),
        STEP_ID_VOTE: service.get_voting_steps(),
        STEP_ID_MAIL_BALLOT: service.get_vote_by_mail_steps(),
    }

    if step_id not in steps_map:
        raise HTTPException(404, "Step '%s' not found" % step_id)

    return steps_map[step_id]
