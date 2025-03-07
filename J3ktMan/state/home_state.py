# import reflex as rx
# from typing import List, Dict, Any
# from J3ktMan.model.project import Project
# from J3ktMan.crud.project import get_projects
# from reflex_clerk import ClerkState
# import datetime


# class HomeState(rx.State):
#     """State for the home page."""

#     # This will be a trigger for refreshes
#     refresh_trigger: int = 0

#     @rx.var
#     async def get_user_projects(self) -> List[Project]:
#         clerk_state = await self.get_state(ClerkState)

#         # If user is not logged in, return empty list
#         if clerk_state.user_id is None:
#             return []

#         # The refresh_trigger will force the computed var to re-run
#         _ = self.refresh_trigger
#         return get_projects(clerk_state.user_id)  # type: ignore

#          # Convert projects to dictionaries with formatted dates
#         result = []
#         for project in projects:
#             # Convert epoch to formatted date string
#             created_date = "Unknown date"
#             if project.created_at is not None:
#                 try:
#                     created_date = datetime.datetime.fromtimestamp(
#                         int(project.created_at)
#                     ).strftime("%Y-%m-%d %H:%M")
#                 except (ValueError, TypeError):
#                     pass

#             # Create a dictionary with all project data plus formatted date
#             project_dict = {
#                 "id": project.id,
#                 "name": project.name,
#                 "created_at": project.created_at,
#                 "created_at_formatted": created_date,
#                 # Add any other fields you need from your Project model
#             }
#             result.append(project_dict)

#         return result

#     def refresh_projects(self):
#         """Increment the refresh trigger to force a refresh"""
#         self.refresh_trigger += 1

import reflex as rx
from typing import List, Dict, Any
from J3ktMan.model.project import Project
from J3ktMan.crud.project import get_projects
from reflex_clerk import ClerkState
import datetime


class HomeState(rx.State):
    """State for the home page."""

    # This will be a trigger for refreshes
    refresh_trigger: int = 0

    @rx.var
    async def get_user_projects(self) -> List[Dict[str, Any]]:
        clerk_state = await self.get_state(ClerkState)

        # If user is not logged in, return empty list
        if clerk_state.user_id is None:
            return []

        # The refresh_trigger will force the computed var to re-run
        _ = self.refresh_trigger
        projects = get_projects(clerk_state.user_id)  # type: ignore

        # Convert projects to dictionaries with formatted dates
        result = []
        for project in projects:
            # Convert epoch to formatted date string
            created_date = "Unknown date"
            if project.created_at is not None:
                try:
                    created_date = datetime.datetime.fromtimestamp(
                        int(project.created_at)
                    ).strftime("%Y-%m-%d %H:%M")
                except (ValueError, TypeError):
                    pass

            # Create a dictionary with all project data plus formatted date
            project_dict = {
                "id": project.id,
                "name": project.name,
                "created_at": project.created_at,
                "created_at_formatted": created_date,
                # Add any other fields you need from your Project model
            }
            result.append(project_dict)

        return result

    def refresh_projects(self):
        """Increment the refresh trigger to force a refresh"""
        self.refresh_trigger += 1
