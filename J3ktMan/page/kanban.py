from __future__ import annotations

from reflex.event import EventSpec
import reflex as rx

import J3ktMan.model.tasks

from J3ktMan.component.drag_zone import drag_zone
from J3ktMan.component.draggable_card import draggable_card
from J3ktMan.component.protected import protected_page_with
from J3ktMan.component.task_dialog import task_dialog, State as TaskDialogState
from J3ktMan.state.project import State as ProjectState, Status
from J3ktMan.component.create_milestone_dialog import (
    create_milestone_dialog,
    State as CreateMilestoneState,
)
from J3ktMan.crud.tasks import (
    delete_status,
)
from J3ktMan.model.project import Project
from J3ktMan.component.base import base_page
from J3ktMan.component.invite_member_dialog import invite_member_dialog
from J3ktMan.model.tasks import Priority


class Task(rx.Base):
    name: str
    description: str
    status_id: int
    milestone_id: int | None
    milestone_name: str | None


class PageData(rx.Base):
    project_id: int
    project: Project


class Milestone(rx.Base):
    model: J3ktMan.model.tasks.Milestone


class EditingStatusName(rx.Base):
    status_id: int
    name: str


class State(rx.State):
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

    @rx.event
    def set_creating_status(self, value: bool) -> None:
        self.creating_status = value

    @rx.event
    def set_filter_milestone_id(self, milestone_id: int | None) -> None:
        self.filter_milestone_id = milestone_id

    @rx.event
    async def create_status(self, form_data) -> list[EventSpec] | None:
        status_name = str(form_data["status_name"])

        project_state = await self.get_state(ProjectState)
        result = project_state.create_status(status_name)

        self.creating_status = False

        return result

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
    async def set_editing_status_name(self, status_id: int) -> None:
        project_state = await self.get_state(ProjectState)
        if project_state.data is None:
            return

        self.editing_status_name = EditingStatusName(
            status_id=status_id,
            name=project_state.data.statuses_by_id[status_id].name,
        )

    @rx.event
    def delete_task(self, task_id: int):
        # remove task from state
        parent_status = self.tasks_by_id[task_id].status_id
        del self.tasks_by_id[task_id]

        # remove task from status
        self.data.statuses_by_id[parent_status].task_ids.remove(task_id)

    @rx.event
    def on_blur_editing_status_name(self) -> None:
        self.editing_status_name = None

    @rx.event
    async def confirm_update_status_name(self) -> list[EventSpec] | None:
        if self.editing_status_name is None:
            return

        project_state = await self.get_state(ProjectState)
        if project_state.data is None:
            return

        status_id = self.editing_status_name.status_id
        new_name = self.editing_status_name.name

        if (
            project_state.data.statuses_by_id[status_id].name
            == self.editing_status_name.name
            or self.editing_status_name.name == ""
        ):
            return

        project_state = await self.get_state(ProjectState)
        result = project_state.rename_status(
            status_id,
            new_name,
        )

        return result

    @rx.event
    async def create_task(self, form_data) -> list[EventSpec] | None:
        if self.creating_task_at is None:
            return

        status_id = self.creating_task_at
        self.creating_task_at = None

        task_name = str(form_data["task_name"])

        project_state = await self.get_state(ProjectState)
        result = project_state.create_task(
            task_name,
            "",
            Priority.MEDIUM,
            status_id,
        )

        return result

    @rx.event
    def cancel_task(self) -> None:
        self.creating_task_at = None

    @rx.var(cache=True)
    def project_name(self) -> str | None:
        return self.page_data.project.name if self.page_data else None

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

    @rx.event
    def on_drag(self, task_id: int) -> None:
        self.dragging_task_id = task_id

    @rx.event
    def on_release(self) -> None:
        self.dragging_task_id = None

    @rx.event
    async def on_drop(self) -> None:
        if self.dragging_task_id is None or self.mouse_over is None:
            self.dragging_task_id = None
            self.mouse_over = None
            return

        project_state = await self.get_state(ProjectState)
        result = project_state.set_task_status(
            self.dragging_task_id, self.mouse_over
        )

        self.dragging_task_id = None
        self.mouse_over = None

        return result

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

    @rx.event
    def test(self):
        print("test")


@rx.page(route="project/kanban/[project_id]")
@protected_page_with(
    on_signed_in=[State.load_project, ProjectState.load_project]
)
def kanban() -> rx.Component:
    return rx.fragment(
        base_page(
            kanban_content(),
        ),
    )


def milestone_menu_item(
    milestone_id: int, milestone_name: str
) -> rx.Component:
    return rx.menu.item(
        rx.icon("list-check", size=12),
        milestone_name,
        on_click=State.set_filter_milestone_id(milestone_id),
    )


def task_card(task_id: int) -> rx.Component:
    return rx.cond(
        ~State.filter_milestone_id  # type: ignore
        | (
            State.filter_milestone_id
            == ProjectState.data.tasks_by_id[task_id].milestone_id  # type: ignore
        )
        | (TaskDialogState.editing_task_id == task_id),
        task_dialog(
            draggable_card(
                rx.dialog.trigger(
                    rx.vstack(
                        rx.text(ProjectState.data.tasks_by_id[task_id].name),  # type: ignore
                        rx.text(
                            ProjectState.data.tasks_by_id[task_id].description,  # type: ignore
                            size="2",
                            color_scheme="gray",
                        ),
                        rx.badge(
                            rx.icon("list-check", size=12),
                            rx.cond(
                                ProjectState.data.tasks_by_id[  # type: ignore
                                    task_id
                                ].milestone_id,
                                ProjectState.data.milestones_by_id[  # type: ignore
                                    ProjectState.data.tasks_by_id[  # type: ignore
                                        task_id
                                    ].milestone_id
                                ].name,
                                "No Milestone",
                            ),
                            variant="soft",
                            color_scheme=rx.cond(
                                ProjectState.data.tasks_by_id[  # type: ignore
                                    task_id
                                ].milestone_id,
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
            ProjectState.data.tasks_by_id[task_id].name,  # type: ignore
            ProjectState.data.tasks_by_id[task_id].description,  # type: ignore
            ProjectState.data.tasks_by_id[task_id].milestone_id,  # type: ignore
            ProjectState.milestone_name_by_ids,
            task_id,
            on_task_name_edit=State.on_task_name_edit,  # type: ignore # type: ignore
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

        state = await self.get_state(ProjectState)
        if state.data is None:
            return []

        return [
            status_id
            for status_id in state.data.statuses_by_id.keys()
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

        state = await self.get_state(ProjectState)
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
                        ProjectState.data.statuses_by_id[  # type: ignore
                            StatusDeleteDialogState.migration_status_id
                        ].name,
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
                    ProjectState.data.statuses_by_id[  # type: ignore
                        status_id
                    ].name,
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
                            st.name,
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
            st.id, e
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
                        & (State.editing_status_name.status_id == st.id),  # type: ignore
                        State.editing_status_name.name,  # type: ignore
                        st.name,
                    ),
                    on_focus=State.set_editing_status_name(st.id),
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
                State.mouse_over == st.id,
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
                State.creating_task_at == st.id,
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
                    on_click=State.set_status_creating_task(st.id),
                ),
            ),
            width="100%",
        ),
        drag_zone(
            position="absolute",
            width=rx.cond(State.is_dragging, "100%", "0"),
            height=rx.cond(State.is_dragging, "100%", "0"),
            on_drag_enter=State.set_mouse_over(st.id),
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
                rx.heading(ProjectState.data.project_name),  # type: ignore
                rx.spacer(),
                rx.hstack(
                    invite_member_dialog(
                        rx.icon_button(
                            "external-link",
                            variant="ghost",
                            color_scheme="gray",
                            size="2",
                        ),
                        ProjectState.data.project_id,  # type: ignore
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
            loading=~ProjectState.loaded,
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
                ),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(
                            rx.icon("chevron-down"),
                            rx.cond(
                                State.filter_milestone_id,
                                (
                                    ProjectState.data.milestones_by_id[  # type: ignore
                                        State.filter_milestone_id
                                    ].name
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
                            ProjectState.milestones,
                            lambda e: milestone_menu_item(e.id, e.name),
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
            loading=~ProjectState.loaded,
        ),
        rx.skeleton(
            rx.scroll_area(
                rx.hstack(
                    rx.foreach(ProjectState.statuses, kanban_column),
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
            loading=~ProjectState.loaded,
        ),
        width="100%",
        height="100%",
    )
