import reflex as rx
import reflex_clerk as clerk
from reflex.event import EventSpec

from J3ktMan.component.base import base_page
from J3ktMan.component.Dashboard.bar_chart import bar_chart
from J3ktMan.component.Dashboard.pie_chart import pie_chart
from J3ktMan.component.Dashboard.dashboard_card import dashboard_card
from J3ktMan.model.project import Project
from J3ktMan.crud.project import get_project, is_in_project, InvalidProjectIDError

class PageData(rx.Base):
    project_id: int
    project: Project

class State(rx.State):
    page_data: PageData | None = None

    @rx.event
    async def load_project(self) -> None | list[EventSpec] | EventSpec:
        if self.page_data is not None:
               return

        clerk_state = await self.get_state(clerk.ClerkState)
        if clerk_state.user_id is None:
            return

        try:
            project_id = int(self.router.page.params["project_id"])
            project = get_project(project_id)

            if not is_in_project(clerk_state.user_id, project_id):
                return [
                    rx.toast.error(
                        "You are not authorized to view this project",
                        position="top-center",
                    ),
                ]
        except (KeyError, ValueError, InvalidProjectIDError):
            return [
                rx.redirect("/"),
                rx.toast.error(
                    "Invalid project ID, Please try again",
                    position="top-center",
                ),
            ]

@rx.page("project/dashboard/[project_id]")
def dashboard() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.text("Dashboard", size="7", weight="bold"),
            rx.hstack(
                rx.box(
                    dashboard_card(name="Completed Projects", icon="circle-check"),
                    width="33%",
                ),
                rx.box(
                    dashboard_card(name="Task created", icon="book-check"),
                    width="33%",
                ),
                rx.box(
                    dashboard_card(name="Task due", icon="calendar-clock"),
                    width="33%",
                ),
                width="100%",
            ),
            rx.spacer(),
            rx.hstack(
                rx.card(
                    rx.text("Priority Breakdown", size="5", weight="bold"),
                    rx.box(
                        bar_chart(),
                    ),
                    padding="4",
                    width="100%",
                    height="300px",
                ),
                rx.card(
                    rx.text("Status overview", size="5", weight="bold"),
                    rx.box(
                        pie_chart(),
                    ),
                    padding="4",
                    height="300px",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            width="100%",
            spacing="4",
        )
    )
