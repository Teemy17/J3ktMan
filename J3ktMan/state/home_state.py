import reflex as rx
from typing import List
from J3ktMan.model.project import Project
from J3ktMan.crud.project import get_projects
from reflex_clerk import ClerkState

class HomeState(rx.State):
    """State for the home page."""

    # This will be a trigger for refreshes
    refresh_trigger: int = 0

    @rx.var
    async def get_user_projects(self) -> List[Project]:
        clerk_state = await self.get_state(ClerkState)

        # If user is not logged in, return empty list
        if clerk_state.user_id is None:
            return []

        # The refresh_trigger will force the computed var to re-run
        _ = self.refresh_trigger
        return get_projects(clerk_state.user_id) #type: ignore

    def refresh_projects(self):
        """Increment the refresh trigger to force a refresh"""
        self.refresh_trigger += 1
