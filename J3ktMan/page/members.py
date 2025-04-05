import reflex as rx

from reflex_clerk.lib.clerk_provider import ClerkState
from typing import Dict
from J3ktMan.component.base import base_page
from J3ktMan.component.protected import protected_page_with

from J3ktMan.crud.project import get_project


class MemberPageState(rx.State):
    project_members: list[Dict[str, str]] = []
    project_name: str = ""

    @rx.var(cache=True)
    def is_loading(self) -> bool:
        return self.page_data is None

    def load_project_members(self):
        """Event handler to load project members"""
        return type(self).get_project_members_async()

    @rx.event
    async def get_project_members_async(self):
        """Get all members of a project with their Clerk user data."""
        from J3ktMan.model.project import ProjectMember

        # Get the project_id from the route params
        project_id = int(self.router.page.params.get("project_id", 0))

        project = get_project(project_id=project_id)
        if project:
            self.project_name = project.name
        else:
            self.project_name = "Unknown Project"

        with rx.session() as session:
            # Get all project members
            members = session.exec(
                ProjectMember.select().where(ProjectMember.project_id == project_id)
            ).all()

            # Initialize an empty result list
            result = []

            # Get Clerk state to access Clerk API
            clerk_state = await self.get_state(ClerkState)

            # For each member, fetch their Clerk user data
            for member in members:
                try:
                    # Get user data from Clerk using the user_id
                    user_data = clerk_state.clerk_api_client.get_user(member.user_id)

                    # Create a member info dictionary with both project member data and user data
                    member_info = {
                        "username": user_data.username,
                        "email": user_data.email_addresses[0].email_address,
                        "role": member.role,
                        "profile_image_url": user_data.profile_image_url,
                    }

                    result.append(member_info)
                except Exception as e:
                    # Handle exceptions (user might not exist in Clerk anymore)
                    print(f"Error fetching user data for {member.user_id}: {e}")

            self.project_members = result


def member_card(member: Dict[str, str]) -> rx.Component:
    """Create a card component for displaying member information."""
    return rx.card(
        rx.flex(
            rx.avatar(
                src=member["profile_image_url"],
                size="4",
            ),
            rx.flex(
                rx.heading(
                    f"{member['username']}",
                    size="3",
                ),
                rx.text(
                    member["email"],
                    color="gray",
                    size="2",
                ),
                rx.badge(
                    member["role"].capitalize(),
                    size="2",
                ),
                width="100%",
                direction="column",
                gap="1",
                justify="center",
                class_name="ml-6",
            ),
            width="100%",
            align="center",
        ),
        width="100%",
        mb="3",
    )


@rx.page(route="/project/members/[project_id]")
@protected_page_with()
def member_page():
    return base_page(
        rx.box(
            rx.heading(
                f"Project / {MemberPageState.project_name}", size="5", weight="bold"
            ),
            rx.divider(),
            rx.heading("Project Members", size="7"),
            rx.cond(
                MemberPageState.project_members,
                rx.hstack(
                    rx.foreach(
                        MemberPageState.project_members,
                        lambda member: member_card(member),
                    ),
                    width="100%",
                    spacing="6",
                    align="stretch",
                    class_name="mt-6",
                ),
                rx.center(
                    rx.vstack(
                        rx.text("No members found for this project.", color="gray"),
                        spacing="2",
                        py="8",
                    )
                ),
            ),
            on_mount=MemberPageState.load_project_members,  # type: ignore
            max_width="800px",
            width="100%",
            mx="auto",
            p="4",
        ),
    )
