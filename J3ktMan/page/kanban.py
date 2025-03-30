from __future__ import annotations

import reflex_clerk as clerk
from reflex.event import EventSpec
import reflex as rx

import J3ktMan.model.tasks

from J3ktMan.component.drag_zone import drag_zone
from J3ktMan.component.draggable_card import draggable_card
from J3ktMan.component.protected import protected_page_with
from J3ktMan.crud.tasks import (
    ExistingMilestoneNameError,
    ExistingStatusNameError,
    ExistingTaskNameError,
    MilestoneCreate,
    assign_milestone,
    create_milestone,
    create_status,
    create_task,
    get_milestone_by_task_id,
    get_milestones_by_project_id,
    get_statuses_by_project_id,
    get_tasks_by_status_id,
    rename_status,
    rename_task,
    set_status,
    set_task_description,
)
from J3ktMan.model.project import Project
from J3ktMan.component.base import base_page
from J3ktMan.component.invite_member_dialog import invite_member_dialog
from J3ktMan.crud.project import (
    InvalidProjectIDError,
    get_project,
    is_in_project,
)
from J3ktMan.model.tasks import Priority


class Task(rx.Base):
    model: J3ktMan.model.tasks.Task
    milestone_id: int | None
    milestone_name: str | None


class Status(rx.Base):
    model: J3ktMan.model.tasks.Status
    task_ids: list[int]


class PageData(rx.Base):
    project_id: int
    project: Project


class Milestone(rx.Base):
    model: J3ktMan.model.tasks.Milestone


class EditingStatusName(rx.Base):
    status_id: int
    name: str


class State(rx.State):
    page_data: PageData | None = None

    dragging_task_id: int | None = None
    """The task ID that is being dragged by."""

    creating_task_at: int | None = None
    """The status ID where the task is being created."""

    mouse_over: int | None = None
    """The status ID where the mouse is over."""

    creating_status: bool = False
    """Whether the user is creating a status."""

    editing_status_name: EditingStatusName | None = None

    tasks_by_id: dict[int, Task] = {}
    statuses_by_id: dict[int, Status] = {}
    milestones_by_id: dict[int, Milestone] = {}

    @rx.event
    def set_creating_status(self, value: bool) -> None:
        self.creating_status = value

    @rx.var(cache=False)
    def milestones(self) -> list[Milestone]:
        return [x for x in self.milestones_by_id.values()]

    @rx.event
    async def create_status(self, form_data) -> list[EventSpec] | None:
        status_name = str(form_data["status_name"])

        if self.page_data is None:
            return

        try:
            status = create_status(status_name, "", self.page_data.project_id)

            self.creating_status = False
            self.statuses_by_id[status.id] = Status(
                model=status,
                task_ids=[],
            )

            return [
                rx.toast.success(
                    f"Status {status_name} has been created",
                    position="top-center",
                )
            ]
        except ExistingStatusNameError:
            return [
                rx.toast.error(
                    f"Status {status_name} already exists",
                    position="top-center",
                )
            ]

    @rx.event
    def set_mouse_over(self, status_id: int) -> None:
        self.mouse_over = status_id

    @rx.event
    def remove_mouse_over(self) -> None:
        self.mouse_over = None

    @rx.event
    def set_status_creating_task(self, status_id: int) -> None:
        self.creating_task_at = status_id

    @rx.event
    def update_status_name(self, name: str) -> None:
        if self.editing_status_name is None:
            return

        self.editing_status_name.name = name

    @rx.event
    def set_editing_status_name(self, status_id: int) -> None:
        if status_id not in self.statuses_by_id:
            return

        self.editing_status_name = EditingStatusName(
            status_id=status_id,
            name=self.statuses_by_id[status_id].model.name,
        )

    @rx.event
    def on_blur_editing_status_name(self) -> None:
        self.editing_status_name = None

    @rx.event
    def confirm_update_status_name(self) -> list[EventSpec] | None:
        if self.editing_status_name is None:
            return

        status_id = self.editing_status_name.status_id
        new_name = self.editing_status_name.name

        if (
            self.statuses[status_id].model.name
            == self.editing_status_name.name
            or self.editing_status_name.name == ""
        ):
            return

        try:
            new_status_model = rename_status(status_id, new_name)
            self.statuses_by_id[status_id].model = new_status_model

            return [
                rx.toast.success(
                    "Status name has been updated", position="top-center"
                ),
            ]

        except ExistingStatusNameError:
            result = [
                rx.toast.error(
                    f"Status `{new_name}` already exists",
                    position="top-center",
                )
            ]

            return result

    @rx.event
    def create_task(self, form_data) -> list[EventSpec] | None:
        if self.creating_task_at is None:
            return

        status_id = self.creating_task_at
        self.creating_task_at = None

        task_name = str(form_data["task_name"])

        if self.page_data is None:
            return

        try:
            # create task
            task = create_task(task_name, "", Priority.MEDIUM, status_id)

            self.tasks_by_id[task.id] = Task(
                model=task, milestone_id=None, milestone_name=None
            )
            self.statuses_by_id[status_id].task_ids.append(task.id)

            return [
                rx.toast.success(
                    f'Task "{task_name}" has been created',
                    position="top-center",
                )
            ]

        except ExistingTaskNameError:
            return [
                rx.toast.error(
                    f'Task "{task_name}" already exists',
                    position="top-center",
                )
            ]

    @rx.event
    def cancel_task(self) -> None:
        self.creating_task_at = None

    @rx.var(cache=True)
    def is_loading(self) -> bool:
        return self.page_data is None

    @rx.var(cache=True)
    def project_name(self) -> str | None:
        return self.page_data.project.name if self.page_data else None

    @rx.var(cache=True)
    def statuses(self) -> list[Status]:
        return [x for x in self.statuses_by_id.values()]

    @rx.event
    def reset_state(self) -> None:
        self.page_data = None
        self.dragging_task_id = None
        self.mouse_over = None
        self.creating_task_at = None
        self.creating_status = False

        self.tasks_by_id = {}
        self.statuses_by_id = {}
        self.milestones_by_id = {}

    @rx.var(cache=False)
    def is_dragging(self) -> bool:
        value = self.dragging_task_id is not None

        return value

    @rx.event
    def set_task_description(
        self, task_id: int, description: str
    ) -> list[EventSpec] | None:
        try:
            new_task_model = set_task_description(task_id, description)

            self.tasks_by_id[task_id].model = new_task_model

            return [
                rx.toast.success(
                    "Task description has been updated", position="top-center"
                ),
            ]

        except Exception:

            return [
                rx.toast.error(
                    "Failed to update task description", position="top-center"
                ),
            ]

    @rx.event
    def rename_task(
        self, task_id: int, new_name: str
    ) -> list[EventSpec] | None:
        try:
            new_task_model = rename_task(task_id, new_name)

            self.tasks_by_id[task_id].model = new_task_model

            return [
                rx.toast.success(
                    "Task has been renamed", position="top-center"
                ),
            ]

        except Exception:
            return [
                rx.toast.error("Failed to rename task", position="top-center"),
            ]

    def is_mouse_over(self, kanban_id: int) -> bool:
        return (
            self.mouse_over == kanban_id
            if self.mouse_over is not None
            else False
        )

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

            statuses = get_statuses_by_project_id(project_id)
            for status in statuses:
                self.statuses_by_id[status.id] = Status(
                    model=status,
                    task_ids=[],
                )

                tasks = get_tasks_by_status_id(status.id)
                for task in tasks:
                    task_milestone = get_milestone_by_task_id(task.id)
                    self.tasks_by_id[task.id] = Task(
                        model=task,
                        milestone_id=(
                            task_milestone.id
                            if task_milestone is not None
                            else None
                        ),
                        milestone_name=(
                            task_milestone.name
                            if task_milestone is not None
                            else None
                        ),
                    )

                    self.statuses_by_id[status.id].task_ids.append(task.id)

            milestones = get_milestones_by_project_id(project_id)
            for milestone in milestones:
                self.milestones_by_id[milestone.id] = Milestone(
                    model=milestone
                )

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

    @rx.event
    def on_drag(self, task_id: int) -> None:
        self.dragging_task_id = task_id

    @rx.event
    def on_release(self) -> None:
        self.dragging_task_id = None

    @rx.event
    def on_drop(self) -> None:
        if (
            self.dragging_task_id is None
            or self.page_data is None
            or self.mouse_over is None
        ):
            self.dragging_task_id = None
            self.mouse_over = None
            return

        task_id = self.dragging_task_id
        previous_status_id = set_status(self.dragging_task_id, self.mouse_over)
        next_status_id = self.mouse_over

        # remove the task from the previous status and add it to the next status
        self.statuses_by_id[previous_status_id].task_ids.remove(task_id)
        self.statuses_by_id[next_status_id].task_ids.append(task_id)

        self.dragging_task_id = None
        self.mouse_over = None

    @rx.event
    def create_milestone(self, form):
        name = str(form["name"])
        description = str(form["description"])

        if self.page_data is None:
            return

        try:
            milestone = create_milestone(
                MilestoneCreate(
                    name=name,
                    description=description,
                    parent_project_id=self.page_data.project_id,
                )
            )

            self.milestones_by_id[milestone.id] = Milestone(model=milestone)

            return [
                rx.toast.success(
                    f"Milestone {name} has been created",
                    position="top-center",
                ),
            ]

        except ExistingMilestoneNameError:
            return [
                rx.toast.error(
                    f"Milestone {name} already exists",
                    position="top-center",
                ),
            ]

    @rx.event
    def assign_milestone(
        self, task_id: int, milestone_id: int | None
    ) -> None | list[EventSpec]:
        assign_milestone(milestone_id, task_id)
        self.tasks_by_id[task_id].milestone_id = milestone_id
        self.tasks_by_id[task_id].milestone_name = (
            self.milestones_by_id[milestone_id].model.name
            if milestone_id is not None
            else None
        )

        message = (
            f'Task "{self.tasks_by_id[task_id].model.name}" has been assigned to "{self.milestones_by_id[milestone_id].model.name}"'
            if milestone_id is not None
            else f'Task "{self.tasks_by_id[task_id].model.name}" has been unassigned'
        )

        return [
            rx.toast.success(message, position="top-center"),
        ]


@rx.page(route="project/kanban/[project_id]")
@protected_page_with(on_signed_in=State.load_project)
def kanban() -> rx.Component:
    return rx.fragment(
        base_page(
            kanban_content(),
        ),
        on_unmount=State.reset_state,
    )


def milestone_menu_item(
    milestone: J3ktMan.model.tasks.Milestone,
) -> rx.Component:
    return rx.menu.item(rx.icon("list-check", size=12), milestone.name)


class TaskDialogState(rx.State):
    editing_task_id: int | None = None
    editing_task_name: str | None = None
    editing_task_description: str | None = None

    @rx.event
    def set_editing_task_id(self, task_id: int, value: bool):
        if value:
            self.editing_task_id = task_id
        else:
            self.reset()

    @rx.event
    def reset_state(self):
        self.editing_task_id = None
        self.editing_task_name = None
        self.editing_task_description = None

    @rx.var(cache=True)
    def is_editing_task_name(self) -> bool:
        return self.editing_task_name is not None

    @rx.var(cache=True)
    def is_editing_task_description(self) -> bool:
        return self.editing_task_description is not None

    @rx.event
    def update_task_editing_name(self, value: str):
        self.editing_task_name = value

    @rx.event
    def update_task_editing_description(self, value: str | None):
        self.editing_task_description = value

    @rx.event
    async def confirm_editing_task_name(self):
        if self.editing_task_id is None or self.editing_task_name is None:
            return

        state = await self.get_state(State)
        state.rename_task(self.editing_task_id, self.editing_task_name)

        self.editing_task_name = None

    @rx.event
    async def confirm_editing_task_description(self):
        if (
            self.editing_task_id is None
            or self.editing_task_description is None
        ):
            return

        state = await self.get_state(State)
        state.set_task_description(
            self.editing_task_id, self.editing_task_description
        )

        self.editing_task_description = None


def task_dialog(task_id: int) -> rx.Component:
    return rx.dialog.content(
        rx.vstack(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="list-todo"),
                    radius="full",
                    padding="0.65rem",
                ),
                rx.cond(
                    TaskDialogState.is_editing_task_name,
                    rx.form(
                        rx.input(
                            value=rx.cond(
                                TaskDialogState.editing_task_name,
                                TaskDialogState.editing_task_name,
                                "",
                            ),
                            variant="soft",
                            background_color="transparent",
                            placeholder="Task Name",
                            auto_focus=True,
                            size="3",
                            content_editable=True,
                            width="100%",
                            on_change=TaskDialogState.update_task_editing_name,
                            on_blur=TaskDialogState.confirm_editing_task_name,
                        ),
                        reset_on_submit=False,
                        on_submit=TaskDialogState.confirm_editing_task_name,
                    ),
                    rx.heading(
                        State.tasks_by_id[task_id].model.name,
                        size="4",
                        width="100%",
                        on_click=TaskDialogState.update_task_editing_name(
                            State.tasks_by_id[task_id].model.name
                        ),
                    ),
                ),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(
                            rx.fragment(
                                rx.cond(
                                    State.tasks_by_id[task_id].milestone_id,
                                    State.tasks_by_id[task_id].milestone_name,
                                    "No Milestone",
                                ),
                                rx.icon("chevron-down", size=12),
                            ),
                            variant="soft",
                            color_scheme=rx.cond(
                                State.tasks_by_id[task_id].milestone_id,
                                "indigo",
                                "gray",
                            ),
                            auto_focus=False,
                        ),
                    ),
                    rx.menu.content(
                        rx.foreach(
                            State.milestones,
                            lambda milestone: rx.menu.item(
                                rx.icon("list-check", size=12),
                                milestone.model.name,
                                cursor="pointer",
                                on_click=State.assign_milestone(
                                    task_id, milestone.model.id
                                ),
                            ),
                        ),
                        rx.menu.separator(),
                        rx.menu.item(
                            "None",
                            color_scheme="gray",
                            on_click=State.assign_milestone(task_id, None),
                        ),
                    ),
                ),
                align_items="center",
                width="100%",
            ),
            rx.heading("Description", size="3", margin_y="0.25rem"),
            rx.cond(
                TaskDialogState.is_editing_task_description,
                rx.box(
                    rx.text_area(
                        TaskDialogState.editing_task_description,
                        width="100%",
                        on_change=TaskDialogState.update_task_editing_description,
                        auto_focus=True,
                        color_scheme="gray",
                        size="2",
                    ),
                    rx.hstack(
                        rx.button(
                            "Save",
                            on_click=TaskDialogState.confirm_editing_task_description,
                            variant="soft",
                            margin_top="1rem",
                        ),
                        rx.button(
                            "Cancel",
                            on_click=TaskDialogState.update_task_editing_description(
                                None
                            ),
                            variant="soft",
                            margin_top="1rem",
                            color_scheme="gray",
                        ),
                    ),
                    width="100%",
                ),
                rx.box(
                    rx.cond(
                        State.tasks_by_id[
                            task_id
                        ].model.description.length()  # type: ignore
                        > 0,
                        rx.text(
                            State.tasks_by_id[task_id].model.description,
                            width="100%",
                            cursor="text",
                            class_name="hover:underline hover:italic",
                        ),
                        rx.text(
                            "No Description, Click to Edit",
                            font_style="italic",
                            color_scheme="gray",
                            width="100%",
                            cursor="text",
                            class_name="hover:underline",
                        ),
                    ),
                    on_click=TaskDialogState.update_task_editing_description(
                        State.tasks_by_id[task_id].model.description
                    ),
                ),
            ),
        ),
        width="80rem",
    )


def task_card(task_id: int) -> rx.Component:
    return rx.dialog(
        draggable_card(
            rx.dialog.trigger(
                rx.vstack(
                    rx.text(State.tasks_by_id[task_id].model.name),
                    rx.text(
                        State.tasks_by_id[task_id].model.description,
                        size="2",
                        color_scheme="gray",
                    ),
                    rx.badge(
                        rx.icon("list-check", size=12),
                        rx.cond(
                            State.tasks_by_id[task_id].milestone_id,
                            State.tasks_by_id[task_id].milestone_name,
                            "No Milestone",
                        ),
                        variant="soft",
                        color_scheme=rx.cond(
                            State.tasks_by_id[task_id].milestone_id,
                            "indigo",
                            "gray",
                        ),
                        cursor="pointer",
                    ),
                ),
            ),
            variant="surface",
            draggable=True,
            cursor="pointer",
            width="100%",
            class_name="round-sm hover:bg-gray-200 dark:hover:bg-zinc-800",
            on_drag_start=State.on_drag(task_id),
            on_drag_end=State.on_release,
        ),
        task_dialog(task_id),
        on_open_change=lambda e: TaskDialogState.set_editing_task_id(
            task_id, e
        ),
    )


def new_kanban_column() -> rx.Component:
    return rx.vstack(
        rx.form(
            rx.input(
                variant="soft",
                background_color="transparent",
                placeholder="Status name",
                auto_focus=True,
                on_blur=State.set_creating_status(False),
                name="status_name",
            ),
            on_submit=State.create_status,
        ),
        rx.divider(),
        width="300px",
        position="relative",
        class_name="dark:bg-zinc-900 rounded-lg p-2 shadow-md",
    )


class StatusDeleteDialogState(rx.State):
    deleting_status_id: int | None = None
    migration_status_id: int | None = None

    @rx.event
    def set_status_delete_dialog(self, status_id: int, e: bool) -> None:
        if e:
            self.deleting_status_id = status_id
            self.migration_status_id = None
        else:
            self.deleting_status_id = None
            self.migration_status_id = None

    @rx.var(cache=True)
    async def get_available_statuses(self) -> list[int]:
        if self.deleting_status_id is None:
            print("early return")
            return []

        state = await self.get_state(State)

        result = [status_id for status_id in state.statuses_by_id.keys()]
        print(f"normal return {result}")
        return result


def migration_status_button(
    st: Status,
) -> rx.Component:
    return rx.menu.root(
        rx.menu.trigger(
            rx.button(
                rx.fragment(
                    rx.cond(
                        StatusDeleteDialogState.migration_status_id,
                        State.statuses_by_id[  # type: ignore
                            StatusDeleteDialogState.migration_status_id
                        ].model.name,
                        "Select Status",
                    ),
                    rx.icon("chevron-down", size=12),
                ),
                variant="soft",
                color_scheme=rx.cond(
                    StatusDeleteDialogState.migration_status_id,
                    "indigo",
                    "gray",
                ),
                auto_focus=False,
            ),
        ),
        rx.menu.content(
            rx.foreach(
                StatusDeleteDialogState.get_available_statuses,  # type: ignore
                lambda milestone: rx.menu.item(
                    rx.icon("list-check", size=12),
                    milestone,
                    cursor="pointer",
                ),
            ),
            rx.menu.separator(),
            rx.menu.item(
                "None",
                color_scheme="gray",
            ),
        ),
    )


def delete_status_dialog(st: Status) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.icon_button(
                "trash-2",
                variant="ghost",
                color_scheme="gray",
                size="2",
            ),
        ),
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.badge(
                        rx.icon(tag="trash-2"),
                        color_scheme="red",
                        radius="full",
                        padding="0.65rem",
                    ),
                    rx.vstack(
                        rx.heading("Delete Status", size="4"),
                        rx.text(
                            "Determine the status to move the tasks to",
                            size="2",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    align_items="center",
                    padding_bottom="1rem",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "Task in the status",
                            size="2",
                            color_scheme="gray",
                            weight="bold",
                        ),
                        rx.badge(
                            st.model.name,
                            variant="soft",
                            color_scheme="red",
                            size="2",
                            padding="0.5rem",
                        ),
                        align_items="left",
                    ),
                    rx.icon(
                        "move-right",
                        color_scheme="gray",
                        class_name="self-center",
                        margin_x="1rem",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.text(
                                "Will be moved to",
                                size="2",
                                color_scheme="gray",
                                weight="bold",
                            ),
                            migration_status_button(st),
                            align_items="left",
                        ),
                    ),
                    class_name="self-center",
                ),
            ),
            width="fit-content",
        ),
        on_open_change=lambda e: StatusDeleteDialogState.set_status_delete_dialog(
            st.model.id, e
        ),
    )


def kanban_column(st: Status) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.form(
                rx.input(
                    variant="soft",
                    background_color="transparent",
                    value=rx.cond(  # type:ignore
                        State.editing_status_name  # type: ignore
                        & (State.editing_status_name.status_id == st.model.id),  # type: ignore
                        State.editing_status_name.name,  # type: ignore
                        st.model.name,
                    ),
                    on_focus=State.set_editing_status_name(st.model.id),
                    on_change=State.update_status_name,
                    on_blur=State.on_blur_editing_status_name,
                ),
                on_submit=State.confirm_update_status_name.prevent_default,
            ),
            rx.spacer(),
            delete_status_dialog(st),
            align="center",
            width="100%",
        ),
        rx.divider(),
        rx.vstack(
            rx.foreach(st.task_ids, task_card),
            rx.cond(
                State.mouse_over == st.model.id,
                rx.box(
                    height="5rem",
                    width="100%",
                    class_name="""
                        rounded-lg dark:border-zinc-600 border border-dashed
                        border-gray-300
                    """,
                ),
            ),
            rx.cond(
                State.creating_task_at == st.model.id,
                rx.card(
                    rx.form(
                        rx.input(
                            auto_focus=True,
                            placeholder="Task name",
                            width="100%",
                            name="task_name",
                            on_blur=State.cancel_task,
                        ),
                        width="100%",
                        on_submit=State.create_task,
                    ),
                    width="100%",
                ),
                rx.icon_button(
                    "plus",
                    variant="ghost",
                    color_scheme="gray",
                    size="2",
                    margin="0.25rem",
                    on_click=State.set_status_creating_task(st.model.id),
                ),
            ),
            width="100%",
        ),
        drag_zone(
            position="absolute",
            width=rx.cond(State.is_dragging, "100%", "0"),
            height=rx.cond(State.is_dragging, "100%", "0"),
            on_drag_enter=State.set_mouse_over(st.model.id),
            on_drag_leave=State.remove_mouse_over,
            on_drag_over=rx.prevent_default,
            on_drop=State.on_drop,
        ),
        width="300px",
        position="relative",
        class_name="bg-gray-50 dark:bg-zinc-900 rounded-lg p-2 shadow-md",
    )


def form_field(
    label: str, placeholder: str, type: str, name: str, is_input: bool
) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.form.label(label),
            (
                rx.form.control(
                    rx.input(placeholder=placeholder, type=type),
                    as_child=True,
                )
                if is_input
                else rx.text_area(placeholder=placeholder, name=name)
            ),
            direction="column",
            spacing="1",
        ),
        name=name,
        width="100%",
    )


def create_milestone_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=12),
                "Add Milestone",
                variant="soft",
                color_scheme="mint",
            ),
        ),
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.badge(
                        rx.icon(tag="list-check"),
                        color_scheme="mint",
                        radius="full",
                        padding="0.65rem",
                    ),
                    rx.vstack(
                        rx.heading("Create Milestone", size="4"),
                        rx.text(
                            "Fill the form to create a new milestone.",
                            size="2",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    align_items="center",
                    padding_bottom="1rem",
                ),
            ),
            rx.form.root(
                rx.flex(
                    form_field(
                        "Name",
                        "Enter milestone name",
                        "text",
                        "name",
                        True,
                    ),
                    form_field(
                        "Description",
                        "Enter milestone description",
                        "text",
                        "description",
                        False,
                    ),
                    rx.dialog.close(
                        rx.button(
                            "Create",
                            type="submit",
                            margin_top="1rem",
                        )
                    ),
                    direction="column",
                ),
                on_submit=State.create_milestone,
            ),
            width="fit-content",
            min_width="20rem",
        ),
    )


def kanban_content() -> rx.Component:
    return rx.vstack(
        rx.skeleton(
            rx.hstack(
                rx.heading(State.project_name),
                rx.spacer(),
                rx.hstack(
                    invite_member_dialog(
                        rx.icon_button(
                            "external-link",
                            variant="ghost",
                            color_scheme="gray",
                            size="2",
                        ),
                        State.page_data.project_id,  # type: ignore
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
                create_milestone_dialog(),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(
                            rx.icon("chevron-down"),
                            rx.text("Milestone"),
                            variant="ghost",
                            weight="medium",
                        ),
                    ),
                    rx.menu.content(
                        rx.foreach(
                            State.milestones,
                            lambda e: milestone_menu_item(e.model),
                        ),
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
                    rx.cond(
                        State.creating_status,
                        new_kanban_column(),
                        rx.icon_button(
                            "book-plus",
                            variant="ghost",
                            color_scheme="gray",
                            size="2",
                            margin="0.25rem",
                            on_click=State.set_creating_status(True),
                        ),
                    ),
                    gap="1rem",
                ),
                type="scroll",
                scrollbars="both",
                padding_bottom="2rem",
                grow="1",
            ),
            loading=State.is_loading,
        ),
        class_name="p-4",
        background_color="gray-100",
    )
