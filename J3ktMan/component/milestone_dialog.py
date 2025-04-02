import reflex as rx
from typing import Any, Dict
from J3ktMan.utils import epoch_to_date


class DateError(Exception):
    pass


class Milestone_Form_State(rx.State):
    """
    State for managing the milestone creation form.
    """

    name: str = ""
    description: str = ""
    due_date: int = 0
    form_data: Dict[str, Any] = {}

    def check_date_validity(self) -> bool:
        """
        Check if the due date is valid.
        """
        if self.due_date <= 0:
            return False
        return True

    @rx.event
    async def submit(self, form: Dict[str, Any]) -> None:
        """
        Handle form submission.
        """
        if not self.check_date_validity():
            raise DateError

        self.form_data = form
        print("Form submitted:", form)


def milestone_creation_dialog() -> rx.Component:
    """
    Dialog popup for creating a new milestone.
    """

    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon(tag="plus"),
                label="Create Milestone",
            )
        ),
        rx.dialog.content(
            rx.dialog.title("Create Milestone"),
            rx.flex(
                rx.form(
                    rx.text(
                        "Milestone name",
                        as_="div",
                        size="2",
                        margin_bottom="3px",
                        weight="bold",
                    ),
                    rx.input(
                        name="name",
                        placeholder="Enter milestone name",
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
                        placeholder="Enter milestone description",
                        required=True,
                        type="text",
                    ),
                    rx.text(
                        "Due date",
                        as_="div",
                        size="2",
                        margin_bottom="3px",
                        weight="bold",
                    ),
                    rx.input(
                        name="due_date",
                        required=True,
                        type="date",
                    ),
                    rx.button(
                        "Create",
                        type="submit",
                        color_scheme="blue",
                        width="100%",
                    ),
                    on_submit=Milestone_Form_State.submit,
                ),
                padding="20px",
            ),
        ),
    )
