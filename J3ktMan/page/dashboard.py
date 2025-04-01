import reflex as rx
import reflex_clerk as clerk
from reflex.event import EventSpec

from J3ktMan.component.base import base_page
from J3ktMan.component.Dashboard.bar_chart import bar_chart
from J3ktMan.component.Dashboard.pie_chart import pie_chart
from J3ktMan.component.Dashboard.dashboard_card import dashboard_card
from J3ktMan.model.project import Project
from J3ktMan.crud.project import get_project, is_in_project, InvalidProjectIDError
from J3ktMan.component.protected import protected_page_with
from J3ktMan.crud.tasks import (
    get_statuses_by_project_id,
    get_tasks_by_status_id,
)


class PageData(rx.Base):
    project_id: int
    project: Project


class State(rx.State):
    page_data: PageData | None = None

    @rx.event
    async def load_project(self) -> None | list[EventSpec] | EventSpec:
        self.page_data = None
        # if self.page_data is not None:
        #     return

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

            new_page_data = PageData(
                project_id=project_id,
                project=project,
            )

            self.page_data = new_page_data

        except (KeyError, ValueError, InvalidProjectIDError):
            return [
                rx.redirect("/"),
                rx.toast.error(
                    "Invalid project ID, Please try again",
                    position="top-center",
                ),
            ]

    @rx.var(cache=True)
    def is_loading(self) -> bool:
        return self.page_data is None

    @rx.event
    def reset_state(self) -> None:
        self.page_data = None

    @rx.var(cache=True)
    def completed_tasks_count(self) -> int:
        if self.page_data is None:
            return 0

        # Get all statuses for this project
        statuses = get_statuses_by_project_id(self.page_data.project_id)

        # Find the "Completed" status (you might need to adjust this logic)
        completed_status = next(
            (status for status in statuses if status.name.lower() == "completed"), None
        )

        if completed_status is None:
            return 0

        # Get tasks with completed status
        completed_tasks = get_tasks_by_status_id(completed_status.id)
        return len(completed_tasks)

    @rx.var(cache=True)
    def total_tasks_count(self) -> int:
        if self.page_data is None:
            return 0

        # Get all statuses for this project
        statuses = get_statuses_by_project_id(self.page_data.project_id)

        # Count tasks across all statuses
        total = 0
        for status in statuses:
            tasks = get_tasks_by_status_id(status.id)
            total += len(tasks)

        return total

    @rx.var(cache=True)
    def pending_tasks_count(self) -> int:
        if self.page_data is None:
            return 0

        # Get all statuses for this project
        statuses = get_statuses_by_project_id(self.page_data.project_id)

        # Find the statuses that indicate pending tasks
        pending_statuses = [
            status
            for status in statuses
            if status.name.lower() in ["in progress", "pending", "to do"]
        ]

        # Count tasks with pending statuses
        total = 0
        for status in pending_statuses:
            tasks = get_tasks_by_status_id(status.id)
            total += len(tasks)

        return total

    @rx.var(cache=True)
    def priority_data(self) -> list:
        # Initialize with default structure
        result = [
            {"name": "Low", "uv": 0},
            {"name": "Medium", "uv": 0},
            {"name": "High", "uv": 0},
        ]

        if self.page_data is None:
            return result

        # Get all statuses for this project
        statuses = get_statuses_by_project_id(self.page_data.project_id)

        # Count tasks by priority
        priority_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}

        for status in statuses:
            tasks = get_tasks_by_status_id(status.id)
            for task in tasks:
                try:
                    priority_name = task.priority.name
                    if priority_name in priority_counts:
                        priority_counts[priority_name] += 1
                except (AttributeError, TypeError):
                    # Handle case where task might not have priority
                    pass

        # Update the default data with actual counts
        return [
            {"name": priority, "uv": count}
            for priority, count in priority_counts.items()
        ]


@rx.page("project/dashboard/[project_id]")
@protected_page_with(on_signed_in=State.load_project)
def dashboard() -> rx.Component:
    return rx.fragment(
        base_page(
            dashboard_content(),
        ),
        on_unmount=State.reset_state,
    )


def dashboard_content() -> rx.Component:
    return rx.vstack(
        rx.text("Dashboard", size="7", weight="bold"),
        rx.skeleton(
            rx.hstack(
                rx.box(
                    dashboard_card(
                        name=f"Completed Tasks: {State.completed_tasks_count}",
                        icon="circle-check",
                    ),
                    width="33%",
                ),
                rx.box(
                    dashboard_card(
                        name=f"Task created: {State.total_tasks_count}",
                        icon="book-check",
                    ),
                    width="33%",
                ),
                rx.box(
                    dashboard_card(
                        name=f"Pending Task: {State.pending_tasks_count}",
                        icon="calendar-clock",
                    ),
                    width="33%",
                ),
                width="100%",
            ),
            loading=State.is_loading,
        ),
        rx.spacer(),
        rx.skeleton(
            rx.hstack(
                rx.card(
                    rx.text("Priority Breakdown", size="5", weight="bold"),
                    rx.box(
                        bar_chart(data=State.priority_data),
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
            loading=State.is_loading,
        ),
        width="100%",
        spacing="4",
    )
