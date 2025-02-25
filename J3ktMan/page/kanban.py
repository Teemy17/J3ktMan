import reflex_clerk as clerk
from reflex.event import EventSpec
import reflex as rx

from J3ktMan.component.drag_zone import drag_zone
from J3ktMan.component.draggable_card import draggable_card
from J3ktMan.component.protected import protected_page_with
from J3ktMan.model.project import Project
from J3ktMan.component.base import base_page
from J3ktMan.crud.project import (
    InvalidProjectIDError,
    get_project,
    is_in_project,
)


class Task(rx.Base):
    id: int
    name: str
    milestone: str


class Status(rx.Base):
    id: int
    name: str
    tasks: list[Task]


class PageData(rx.Base):
    project_id: int
    project: Project
    statuses: list


class State(rx.State):
    _page_data: PageData | None = None
    _dragging_task_id: int | None = None
    mouse_over: int | None = None

    @rx.event
    def set_mouse_over(self, status_id: int) -> None:
        self.mouse_over = status_id

    @rx.event
    def remove_mouse_over(self) -> None:
        self.mouse_over = None

    @rx.var(cache=False)
    def is_loading(self) -> bool:
        return self._page_data is None

    @rx.var(cache=False)
    def project_name(self) -> str | None:
        return self._page_data.project.name if self._page_data else None

    @rx.var(cache=False)
    def statuses(self) -> list[Status]:
        return [] if self._page_data is None else self._page_data.statuses

    @rx.event
    def reset_state(self) -> None:
        self._page_data = None
        self._dragging_task_id = None
        self.mouse_over = None

    @rx.var(cache=False)
    def is_dragging(self) -> bool:
        value = self._dragging_task_id is not None

        return value

    def is_mouse_over(self, kanban_id: int) -> bool:
        return (
            self.mouse_over == kanban_id
            if self.mouse_over is not None
            else False
        )

    @rx.event
    async def load_project(self) -> None | list[EventSpec] | EventSpec:
        if self._page_data is not None:
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

            self._page_data = PageData(
                project_id=project_id,
                project=project,
                statuses=[
                    Status(
                        id=0,
                        name="Todo",
                        tasks=[
                            Task(
                                id=0,
                                name="Create a fucking python project this gonna be a long one",
                                milestone="Milestone 1",
                            ),
                            Task(
                                id=1,
                                name="Create a fucking python project this gonna be a long one",
                                milestone="Milestone 1",
                            ),
                            Task(
                                id=2,
                                name="Create a fucking python project this gonna be a long one",
                                milestone="Milestone 1",
                            ),
                            Task(
                                id=3,
                                name="Create a fucking python project this gonna be a long one",
                                milestone="Milestone 1",
                            ),
                            Task(
                                id=4,
                                name="Create a fucking python project this gonna be a long one",
                                milestone="Milestone 1",
                            ),
                            Task(
                                id=5,
                                name="Create a fucking python project this gonna be a long one",
                                milestone="Milestone 1",
                            ),
                        ],
                    ),
                    Status(id=1, name="In Progress", tasks=[]),
                    Status(id=2, name="Done", tasks=[]),
                ],
            )

        except (KeyError, ValueError, InvalidProjectIDError):
            return [
                rx.redirect("/"),
                rx.toast.error(
                    "Invalid project ID, Please try again",
                    position="top-center",
                ),
            ]

        pass

    @rx.event
    def on_drag(self, task_id: int) -> None:
        self._dragging_task_id = task_id

    @rx.event
    def on_release(self) -> None:
        self._dragging_task_id = None


@rx.page(route="project/kanban/[project_id]")
@protected_page_with(on_signed_in=State.load_project)
def kanban() -> rx.Component:
    return rx.fragment(
        base_page(
            kanban_content(),
        ),
        on_unmount=State.reset_state,
    )


def task_card(task: Task) -> rx.Component:
    return draggable_card(
        rx.vstack(
            rx.text(task.name),
            rx.badge(task.milestone, variant="soft"),
        ),
        variant="surface",
        draggable=True,
        width="100%",
        class_name=f"round-sm{task.id}",
        on_drag_start=State.on_drag(task.id),
        on_drag_end=State.on_release,
    )


def kanban_column(status: Status) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.input(
                variant="soft",
                background_color="transparent",
                value=status.name,
            ),
            rx.spacer(),
            rx.icon_button(
                "ellipsis", variant="ghost", color_scheme="gray", size="2"
            ),
            align="center",
            width="100%",
        ),
        rx.divider(),
        rx.cond(
            State.mouse_over == status.id,
            rx.box(
                height="5rem",
                width="100%",
                class_name="""
                    rounded-lg dark:border-zinc-600 border border-dashed
                """,
            ),
        ),
        rx.vstack(
            rx.foreach(status.tasks, task_card),
            rx.icon_button(
                "plus",
                variant="ghost",
                color_scheme="gray",
                size="2",
                margin="0.25rem",
            ),
        ),
        drag_zone(
            position="absolute",
            width=rx.cond(State.is_dragging, "100%", "0"),
            height=rx.cond(State.is_dragging, "100%", "0"),
            on_drag_enter=State.set_mouse_over(status.id),
            on_drag_leave=State.remove_mouse_over,
        ),
        width="300px",
        position="relative",
        class_name="dark:bg-zinc-900 rounded-lg p-2 shadow-md",
    )


def kanban_content() -> rx.Component:
    return rx.vstack(
        rx.skeleton(
            rx.hstack(
                rx.heading(State.project_name),
                rx.spacer(),
                rx.hstack(
                    rx.icon_button(
                        "external-link",
                        variant="ghost",
                        color_scheme="gray",
                        size="2",
                    ),
                    rx.icon_button(
                        "ellipsis",
                        variant="ghost",
                        color_scheme="gray",
                        size="2",
                    ),
                ),
                width="100%",
                align="center",
            ),
            loading=State.is_loading,
        ),
        rx.skeleton(
            rx.hstack(
                rx.input(
                    rx.input.slot(rx.icon("search")),
                    placeholder="Search...",
                    type="search",
                    size="2",
                    justify="end",
                ),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(
                            rx.text("Milestone"),
                            rx.icon("chevron-down"),
                            variant="ghost",
                            weight="medium",
                        ),
                    ),
                    rx.menu.content(
                        rx.menu.item("Milestone 1"),
                        rx.menu.item("Milestone 2"),
                        rx.menu.item("Milestone 3"),
                    ),
                    justify="end",
                ),
                gap="1rem",
                margin_top="2rem",
                margin_bottom="1rem",
                align="center",
            ),
            loading=State.is_loading,
        ),
        rx.skeleton(
            rx.scroll_area(
                rx.hstack(
                    rx.foreach(State.statuses, kanban_column),
                    gap="1rem",
                ),
                scrollbars="both",
            ),
            loading=State.is_loading,
        ),
        class_name="p-4",
        background_color="gray-100",
    )
