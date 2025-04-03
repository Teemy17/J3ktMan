import reflex as rx
from typing import Any, Dict, List
from J3ktMan.utils import epoch_to_date, date_to_epoch
from J3ktMan.state.project import State as ProjectState
from J3ktMan.state.project import Task


class DropdownState(rx.State):
    which_dialog_open: str = ""
    current_task_id: int = 0

    def set_which_dialog_open(self, value: str):
        self.which_dialog_open = value

    @rx.event
    async def delete(self, task_id: int) -> None:
        """
        Delete the task with the given ID.
        """
        state = await self.get_state(ProjectState)
        return state.delete_task(task_id)

    @rx.event
    async def edit(self, form_data: Dict[str, Any]) -> None:
        """
        Handle edit form submission
        """
        state = await self.get_state(ProjectState)
        await state.edit_task(
            task_id=int(form_data["task_id"]),  # type: ignore
            name=str(form_data["name"]),
            description=str(form_data["description"]),
            start_date=date_to_epoch(form_data["start_date"]),
            end_date=date_to_epoch(form_data["end_date"]),
        )
        self.which_dialog_open = ""  # Close dialog after edit


class TaskEditState(rx.State):
    """
    State for editing a task.
    """

    name: str = ""
    description: str = ""
    start_date: str = ""
    end_date: str = ""
    task_id: int = 0

    async def on_mount(self, task_id: int) -> None:
        """
        Set the initial state of the form.
        """
        state = await self.get_state(ProjectState)
        await state.load_project()
        task = state.tasks.get(task_id)
        if task:
            self.task_id = task.id
            self.name = task.name
            self.description = task.description
            self.start_date = epoch_to_date(task.start_date)  # type: ignore
            self.end_date = epoch_to_date(task.end_date)  # type: ignore


def delete_dialog(task_id: int) -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Are you Sure?"),
            rx.alert_dialog.description(
                rx.text(
                    "This action cannot be undone. Are you sure you want to delete this item?",
                ),
                margin_bottom="20px",
            ),
            rx.hstack(
                rx.alert_dialog.action(
                    rx.button(
                        "Delete",
                        color_scheme="red",
                        on_click=DropdownState.delete(task_id),
                    ),
                ),
                rx.spacer(),
                rx.alert_dialog.cancel(rx.button("Cancel")),
            ),
        ),
        open=DropdownState.which_dialog_open == "delete",
        on_open_change=DropdownState.set_which_dialog_open(""),  # type:ignore
    )


def edit_dialog(task_id: int) -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="list-check"),
                    color_scheme="mint",
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.alert_dialog.title("Edit Task"),
                    rx.alert_dialog.description(
                        rx.text(
                            f"Edit task details",
                        ),
                        margin_bottom="20px",
                    ),
                    spacing="1",
                    align_items="start",
                ),
                align_items="center",
                padding_bottom="1rem",
            ),
            rx.form.root(
                rx.flex(
                    rx.input(
                        name="name",
                        placeholder="Enter task name",
                        required=True,
                        type="text",
                        default_value=TaskEditState.name,
                    ),
                    rx.input(
                        name="description",
                        placeholder="Enter description",
                        type="text",
                        default_value=TaskEditState.description,
                    ),
                    rx.input(
                        name="start_date",
                        placeholder="Enter start date",
                        required=True,
                        type="date",
                        default_value=TaskEditState.start_date,
                    ),
                    rx.input(
                        name="end_date",
                        placeholder="Enter end date",
                        type="date",
                        default_value=TaskEditState.end_date,
                    ),
                    rx.input(
                        name="task_id",
                        class_name="hidden",
                        value=TaskEditState.task_id,
                    ),
                    rx.button(
                        "Edit",
                        type="submit",
                        margin_top="1rem",
                        color_scheme="blue",
                        class_name="w-full",
                        padding="1rem",
                        border_radius="0.5rem",
                    ),
                    direction="column",
                    spacing="1",
                    margin_bottom="1rem",
                    class_name="w-full",
                    padding="1rem",
                    border_radius="0.5rem",
                ),
                on_submit=DropdownState.edit,  # type: ignore
                reset_on_submit=True,
            ),
            rx.spacer(direction="column"),
            rx.alert_dialog.cancel(rx.button("Cancel")),
        ),
        on_mount=TaskEditState.on_mount(task_id),  # type:ignore
        open=DropdownState.which_dialog_open == "edit",
        on_open_change=DropdownState.set_which_dialog_open(""),  # type:ignore
    )


def task_elipsis(task: Task) -> rx.Component:
    """
    Ellipsis button -> dropdown widget for each task.
    """
    return rx.vstack(
        rx.menu.root(
            rx.menu.trigger(
                rx.button(
                    rx.icon(tag="ellipsis", size=14),
                    size="1",
                    variant="ghost",
                    color_scheme="gray",
                    class_name="mx-1",
                )
            ),
            rx.menu.content(
                rx.menu.item(
                    "Edit",
                    on_click=lambda: DropdownState.set_which_dialog_open(
                        "edit"  # type:ignore
                    ),
                ),
                rx.menu.item(
                    "Delete",
                    on_click=lambda: DropdownState.set_which_dialog_open(
                        "delete"  # type:ignore
                    ),
                ),
            ),
        ),
        delete_dialog(task.id),
        edit_dialog(task.id),
        align="center",
    )
