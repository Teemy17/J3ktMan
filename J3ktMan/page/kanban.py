from __future__ import annotations

import reflex_clerk as clerk
from reflex.event import EventSpec
import reflex as rx

import J3ktMan.model.tasks

from J3ktMan.component.drag_zone import drag_zone
from J3ktMan.component.draggable_card import draggable_card
from J3ktMan.component.protected import protected_page_with
from J3ktMan.component.task_dialog import task_dialog, State as TaskDialogState
from J3ktMan.component.create_milestone_dialog import (
    create_milestone_dialog,
    State as CreateMilestoneState,
)
from J3ktMan.crud.tasks import (
    ExistingStatusNameError,
    ExistingTaskNameError,
    delete_status,
    create_status,
    create_task,
    get_milestone_by_task_id,
    get_milestones_by_project_id,
    get_statuses_by_project_id,
    get_tasks_by_status_id,
    rename_status,
    set_status,
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
    name: str
    description: str
    status_id: int
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

    filter_milestone_id: int | None = None
    """The milestone ID that is being filtered by."""

    editing_status_name: EditingStatusName | None = None

    tasks_by_id: dict[int, Task] = {}
    statuses_by_id: dict[int, Status] = {}
    milestones_by_id: dict[int, Milestone] = {}

    @rx.event
    def set_creating_status(self, value: bool) -> None:
        self.creating_status = value

    @rx.var(cache=True)
    def milestones(self) -> list[Milestone]:
        return [x for x in self.milestones_by_id.values()]

    @rx.var(cache=True)
    def milestone_name_by_ids(self) -> dict[int, str]:
        result = {}
        for id, mil in self.milestones_by_id.items():
            result[id] = mil.model.name

        return result

    @rx.event
    def set_filter_milestone_id(self, milestone_id: int | None) -> None:
        self.filter_milestone_id = milestone_id

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
    def delete_task(self, task_id: int):
        # remove task from state
        parent_status = self.tasks_by_id[task_id].status_id
        del self.tasks_by_id[task_id]

        # remove task from status
        self.statuses_by_id[parent_status].task_ids.remove(task_id)

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
            self.statuses_by_id[status_id].model.name
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
                name=task.name,
                description=task.description,
                status_id=task.status_id,
                milestone_id=None,
                milestone_name=None,
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
    def delete_status(
        self, status_id: int, migration_status_id: int
    ) -> list[EventSpec]:
        if status_id not in self.statuses_by_id:
            return []

        # delete status
        affecting_tasks = delete_status(status_id, migration_status_id)

        # remove status from state
        deleted_status_name = self.statuses_by_id[status_id].model.name
        del self.statuses_by_id[status_id]

        # remove tasks from state
        for affecting_task in affecting_tasks:
            self.tasks_by_id[affecting_task.id].model = affecting_task

            self.statuses_by_id[migration_status_id].task_ids.append(
                affecting_task.id
            )

        return [
            rx.toast.success(
                f"Status {deleted_status_name} has been deleted",
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

    @rx.var(cache=False)
    def is_dragging(self) -> bool:
        value = self.dragging_task_id is not None

        return value

    @rx.event
    async def on_task_description_edit(self):
        task_diag_state = await self.get_state(TaskDialogState)
        task_id = task_diag_state.editing_task_id
        task_description_set = task_diag_state.last_task_description_set

        if task_description_set and task_id:
            self.tasks_by_id[task_id].description = task_description_set

    @rx.event
    async def on_task_name_edit(self):
        task_diag_state = await self.get_state(TaskDialogState)
        task_id = task_diag_state.editing_task_id
        new_name = task_diag_state.last_task_renamed

        if new_name and task_id:
            self.tasks_by_id[task_id].name = new_name

    def is_mouse_over(self, kanban_id: int) -> bool:
        return (
            self.mouse_over == kanban_id
            if self.mouse_over is not None
            else False
        )

    @rx.event
    async def load_project(self) -> None | list[EventSpec] | EventSpec:
        self.reset()

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
                        name=task.name,
                        description=task.description,
                        status_id=task.status_id,
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
    async def on_create_milestone(self):
        if self.page_data is None:
            return

        create_milestone_state = await self.get_state(CreateMilestoneState)
        milestone = create_milestone_state.last_created_milestone

        if milestone is None:
            return

        self.milestones_by_id[milestone.id] = Milestone(model=milestone)

    @rx.event
    async def assign_milestone(self) -> None | list[EventSpec]:
        task_diag_state = await self.get_state(TaskDialogState)
        task_id = task_diag_state.editing_task_id
        milestone_id = task_diag_state.last_assigned_milestone_id

        if task_id is None:
            return

        self.tasks_by_id[task_id].milestone_id = milestone_id
        self.tasks_by_id[task_id].milestone_name = (
            self.milestones_by_id[milestone_id].model.name
            if milestone_id is not None
            else None
        )


@rx.page(route="project/kanban/[project_id]")
@protected_page_with(on_signed_in=State.load_project)
def kanban() -> rx.Component:
    return rx.fragment(
        base_page(
            kanban_content(),
        ),
    )


def milestone_menu_item(
    milestone: J3ktMan.model.tasks.Milestone,
) -> rx.Component:
    return rx.menu.item(
        rx.icon("list-check", size=12),
        milestone.name,
        on_click=State.set_filter_milestone_id(milestone.id),
    )


def task_card(task_id: int) -> rx.Component:
    return rx.cond(
        ~State.filter_milestone_id  # type: ignore
        | (
            State.filter_milestone_id
            == State.tasks_by_id[task_id].milestone_id
        )
        | (TaskDialogState.editing_task_id == task_id),
        task_dialog(
            draggable_card(
                rx.dialog.trigger(
                    rx.vstack(
                        rx.text(State.tasks_by_id[task_id].name),
                        rx.text(
                            State.tasks_by_id[task_id].description,
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
                class_name=(  # type: ignore
                    "round-sm "
                    + rx.color_mode_cond(
                        dark="hover:bg-zinc-800",
                        light="hover:bg-gray-200",
                    )
                ),
                on_drag_start=State.on_drag(task_id),
                on_drag_end=State.on_release,
            ),
            State.tasks_by_id[task_id].name,
            State.tasks_by_id[task_id].description,
            State.tasks_by_id[task_id].milestone_id,
            State.milestone_name_by_ids,
            task_id,
            on_task_name_edit=State.on_task_name_edit,
            on_task_description_edit=State.on_task_description_edit,
            on_assign_milestone=State.assign_milestone,
            on_delete_task=State.delete_task(task_id),
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
        class_name=(  # type: ignore
            "rounded-lg p-2 shadow-md "
            + rx.color_mode_cond(
                dark="bg-zinc-900",
                light="bg-gray-50",
            )
        ),
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
            return []

        state = await self.get_state(State)

        return [
            status_id
            for status_id in state.statuses_by_id.keys()
            if status_id != self.deleting_status_id
        ]

    @rx.event
    async def set_migration_status(self, status_id: int | None) -> None:
        self.migration_status_id = status_id

    @rx.event
    async def confirm_delete_status(self) -> list[EventSpec]:
        if self.deleting_status_id is None or self.migration_status_id is None:
            return [
                rx.toast.error(
                    "Please select a status to move the tasks to",
                    position="top-center",
                )
            ]

        state = await self.get_state(State)
        result = state.delete_status(
            self.deleting_status_id, self.migration_status_id
        )

        self.deleting_status_id = None
        self.migration_status_id = None

        return result


def migration_status_button() -> rx.Component:
    return rx.menu.root(
        rx.menu.trigger(
            rx.button(
                rx.hstack(
                    rx.cond(
                        StatusDeleteDialogState.migration_status_id,
                        State.statuses_by_id[  # type: ignore
                            StatusDeleteDialogState.migration_status_id
                        ].model.name,
                        "Select Status",
                    ),
                    rx.spacer(),
                    rx.icon("chevron-down", size=12),
                    width="100%",
                    class_name="items-center self-center",
                ),
                variant="outline",
                color_scheme=rx.cond(
                    StatusDeleteDialogState.migration_status_id,
                    "indigo",
                    "gray",
                ),
                width="100%",
                auto_focus=False,
            ),
        ),
        rx.menu.content(
            rx.foreach(
                StatusDeleteDialogState.get_available_statuses,  # type: ignore
                lambda status_id: rx.menu.item(
                    rx.icon("git-commit-horizontal", size=12),
                    State.statuses_by_id[status_id].model.name,
                    cursor="pointer",
                    on_click=StatusDeleteDialogState.set_migration_status(
                        status_id
                    ),
                ),
            ),
            rx.menu.separator(),
            rx.menu.item(
                "None",
                color_scheme="gray",
                on_click=StatusDeleteDialogState.set_migration_status(None),
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
                        rx.button(
                            st.model.name,
                            variant="outline",
                            color_scheme="red",
                            auto_focus=False,
                            clickable=False,
                        ),
                        align_items="left",
                        class_name="flex-1",
                    ),
                    rx.icon(
                        "move-right",
                        color_scheme="gray",
                        class_name="self-center",
                        margin_x="1rem",
                    ),
                    rx.vstack(
                        rx.text(
                            "Will be moved to",
                            size="2",
                            color_scheme="gray",
                            weight="bold",
                        ),
                        migration_status_button(),
                        align_items="left",
                        class_name="flex-1",
                    ),
                    class_name="self-center",
                    width="100%",
                ),
                rx.dialog.close(
                    rx.hstack(
                        rx.button(
                            "Cancel",
                            variant="soft",
                            color_scheme="gray",
                            auto_focus=False,
                        ),
                        rx.button(
                            "Delete",
                            variant="soft",
                            color_scheme="red",
                            auto_focus=False,
                            on_click=StatusDeleteDialogState.confirm_delete_status,
                        ),
                        class_name="self-end items-center mt-1",
                    ),
                ),
            ),
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
        class_name=(  # type: ignore
            "rounded-lg p-2 shadow-md "
            + rx.color_mode_cond(dark="bg-zinc-900", light="bg-gray-50")
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
                create_milestone_dialog(
                    rx.button(
                        rx.icon("plus", size=12),
                        "Add Milestone",
                        variant="soft",
                        color_scheme="mint",
                    ),
                    State.page_data.project_id,  # type: ignore
                    State.on_create_milestone,
                ),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(
                            rx.icon("chevron-down"),
                            rx.cond(
                                State.filter_milestone_id,
                                (
                                    State.milestones_by_id[
                                        State.filter_milestone_id
                                    ].model.name  # type: ignore
                                ),
                                "All Milestones",
                            ),
                            variant=rx.cond(
                                State.filter_milestone_id, "soft", "ghost"
                            ),
                            weight="medium",
                            color_scheme=rx.cond(
                                State.filter_milestone_id, "indigo", "gray"
                            ),
                        ),
                    ),
                    rx.menu.content(
                        rx.foreach(
                            State.milestones,
                            lambda e: milestone_menu_item(e.model),
                        ),
                        rx.menu.separator(),
                        rx.menu.item(
                            "None",
                            color_scheme="gray",
                            on_click=State.set_filter_milestone_id(None),
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
                    margin_bottom="1rem",
                ),
                type="scroll",
                scrollbars="both",
                grow="1",
            ),
            loading=State.is_loading,
        ),
        width="100%",
        height="100%",
    )

