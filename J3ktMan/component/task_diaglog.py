import reflex as rx
from typing import Any, Dict
from J3ktMan.utils import epoch_to_date


class Task_Form_State(rx.State):
    """
    State for managing the task creation form.
    """

    name: str = ""
    description: str = ""
    priority: str = "LOW"
    start_date: int = 0
    end_date: int = 0
    form_data: Dict[str, Any] = {}

    def check_date_validity(self) -> bool:
        """
        Check if the start date is before the end date.
        """
        if self.start_date >= self.end_date:
            return False
        return True

    @rx.event
    async def submit(self, form: Dict[str, Any]) -> None:
        """
        Handle form submission.
        """
        self.form_data = form
        print("Form submitted:", form)


class PriorityState(rx.State):
    """
    State for managing the priority selection.
    """

    values: list[str] = ["LOW", "MEDIUM", "HIGH"]
    value: str = "LOW"

    @rx.event
    def set_value(self, value: str) -> None:
        """
        Set the selected priority value.
        """
        self.value = value


def task_creation_dialog() -> rx.Component:
    """
    Dialog popup for creating a new task.
    """

    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon(tag="plus"),
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("Create Task"),
            rx.flex(
                rx.form(
                    rx.text(
                        "Task name",
                        as_="div",
                        size="2",
                        margin_bottom="3px",
                        weight="bold",
                    ),
                    rx.input(
                        name="name",
                        placeholder="Enter task name",
                        required=True,
                        type="text",
                    ),
                    rx.text(
                        "Description",
                        as_="div",
                        size="2",
                        margin_bottom="3px",
                        weight="bold",
                    ),
                    rx.input(
                        name="description",
                        placeholder="Enter description",
                        type="text",
                    ),
                    rx.text(
                        "Start Date",
                        as_="div",
                        size="2",
                        margin_bottom="3px",
                        weight="bold",
                    ),
                    rx.input(
                        name="start_date",
                        placeholder="Enter start date",
                        required=True,
                        type="date",
                    ),
                    rx.text(
                        "End Date",
                        as_="div",
                        size="2",
                        margin_bottom="3px",
                        weight="bold",
                    ),
                    rx.input(
                        name="end_date",
                        placeholder="Enter end date",
                        required=True,
                        type="date",
                    ),
                    rx.text(
                        "Select Priority",
                        as_="div",
                        size="2",
                        margin_bottom="3px",
                        weight="bold",
                    ),
                    rx.select(
                        PriorityState.values,
                        value=PriorityState.value,
                        on_change=PriorityState.set_value,
                    ),
                    rx.button(
                        "Create Task",
                        color_scheme="blue",
                    ),
                    on_submit=Task_Form_State.submit,
                ),
                direction="column",
                spacing="3",
            ),
        ),
    )
