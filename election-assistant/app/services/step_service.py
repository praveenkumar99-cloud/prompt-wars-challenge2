"""Module: step_service.py
Description: Step-by-step election guidance service.
Author: Praveen Kumar
"""
__all__ = ["StepService"]

from typing import List

from ..constants import STEP_ID_MAIL_BALLOT, STEP_ID_REGISTER, STEP_ID_VOTE
from ..models import ElectionStep


class StepService:
    """Service for providing step-by-step election guidance."""

    def get_registration_steps(self) -> ElectionStep:
        """Get steps for voter registration.

        Returns:
            ElectionStep object for registration process.
        """
        return ElectionStep(
            step_id=STEP_ID_REGISTER,
            title="How to Register to Vote",
            description="Follow these steps to register to vote in your state.",
            actions=[
                "Check your eligibility (US citizen, state resident, 18+ by Election Day)",
                "Gather required information (driver's license, SSN, proof of residency)",
                "Choose registration method: online, by mail, or in-person",
                "Complete the voter registration form",
                "Submit before your state's deadline",
                "Verify your registration status after 2-3 weeks",
            ],
            estimated_time="10-15 minutes",
            resources=[
                "USA.gov voter registration",
                "Your state's election website",
                "National Voter Registration Form",
            ],
        )

    def get_voting_steps(self) -> ElectionStep:
        """Get steps for voting in person.

        Returns:
            ElectionStep object for voting process.
        """
        return ElectionStep(
            step_id=STEP_ID_VOTE,
            title="How to Vote",
            description="Steps to cast your ballot successfully.",
            actions=[
                "Check your registration status",
                "Research candidates and ballot measures",
                "Decide voting method: in-person early, Election Day, or by mail",
                "If voting by mail: request, complete, and return ballot before deadline",
                "If voting in person: find your polling place and hours",
                "Bring required ID (check your state's requirements)",
                "Cast your ballot and confirm it's counted",
            ],
            estimated_time="15-30 minutes (plus research time)",
            resources=[
                "Ballotpedia for candidate research",
                "Your state's sample ballot",
                "Local election office contact",
            ],
        )

    def get_vote_by_mail_steps(self) -> ElectionStep:
        """Get steps for voting by mail.

        Returns:
            ElectionStep object for mail voting process.
        """
        return ElectionStep(
            step_id=STEP_ID_MAIL_BALLOT,
            title="How to Vote by Mail",
            description="Complete guide to absentee and mail voting.",
            actions=[
                "Request mail ballot from your state election office",
                "Receive ballot package in mail",
                "Read instructions carefully",
                "Mark your ballot in a private space",
                "Sign and seal ballot envelope (required)",
                "Return ballot by mail or official drop box",
                "Track your ballot online if available",
            ],
            estimated_time="Request: 5 min, Complete: 15 min",
            resources=[
                "Absentee ballot request form",
                "USPS election mail guidelines",
                "Ballot tracking website",
            ],
        )

    def get_all_steps(self) -> List[ElectionStep]:
        """Get all step-by-step guides.

        Returns:
            List of all ElectionStep objects.
        """
        return [
            self.get_registration_steps(),
            self.get_voting_steps(),
            self.get_vote_by_mail_steps(),
        ]
