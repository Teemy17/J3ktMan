import reflex as rx
from typing import Any, Dict, List
from J3ktMan.utils import date_to_epoch
from J3ktMan.state.project import State as ProjectState
from J3ktMan.model.tasks import Priority


class DateError(Exception):
    pass


class Task_Form_State(rx.State):
    which_dialog_open: str = ""

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
        name: str = str(form["name"])
        description: str = str(form["description"])
        start_date: int = date_to_epoch(form["start_date"])
        end_date: int = date_to_epoch(form["end_date"])
        priority: Priority = Priority(str(form["priority"]))
        milestone_id: int = int(form["milestone_id"])

        # Get the selected status from TaskStatusState
        task_status_state = await self.get_state(TaskStatusState)
        status_id: int = task_status_state.statuses[form["status"]]

        state = await self.get_state(ProjectState)
        created_task = state.create_task(
            name,
            description,
            priority,
            status_id,
            milestone_id,
            start_date,
            end_date,
        )

        return created_task

    @rx.event
    def set_which_dialog_open(self, value: str) -> None:
        """
        Set the dialog open state.
        """
        self.which_dialog_open = value


class PriorityState(rx.State):

    values: list[str] = ["LOW", "MEDIUM", "HIGH"]
    value: str = "LOW"

    @rx.event
    def set_value(self, value: str) -> None:
        """
        Set the selected priority value.
        """
        self.value = value


class TaskStatusState(rx.State):
    statuses: Dict[str, int] = {}
    value: str = "-"

    @rx.var
    async def values(self) -> List[str]:
        state = await self.get_state(ProjectState)
        for status in state.statuses:
            self.statuses[status.name] = status.id
        return [status.name for status in state.statuses]

    @rx.event
    def set_value(self, value: str) -> None:
        """
        Set the selected status value.
        """
        self.value = value


def create_task_dialog(milestone) -> rx.Component:
    """
    Dialog popup for creating a new task.
    """

    return (
        rx.alert_dialog.root(
            rx.alert_dialog.trigger(
                rx.button(
                    rx.icon(tag="plus", size=14),
                    size="1",
                    variant="ghost",
                    color_scheme="gray",
                    class_name="mx-1",
                ),
            ),
            rx.alert_dialog.content(
                rx.vstack(
                    rx.hstack(
                        rx.badge(
                            rx.icon(tag="list-todo"),
                            radius="full",
                            padding="0.65rem",
                        ),
                        rx.vstack(
                            rx.alert_dialog.title("Create Task"),
                            rx.alert_dialog.description(
                                f'Create new Task under milestone "{milestone.name}"'
                            ),
                            spacing="1",
                        ),
                    ),
                    rx.form.root(
                        rx.text(
                            "Task name",
                            as_="div",
                            size="2",
                            margin_bottom="4px",
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
                            margin_bottom="4px",
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
                            margin_bottom="4px",
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
                            margin_bottom="4px",
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
                            margin_bottom="4px",
                            weight="bold",
                        ),
                        rx.select(
                            PriorityState.values,
                            value=PriorityState.value,
                            on_change=PriorityState.set_value,
                            name="priority",
                        ),
                        rx.text(
                            "Select Status",
                            as_="div",
                            size="2",
                            margin_bottom="4px",
                            weight="bold",
                        ),
                        rx.select(
                            TaskStatusState.values,
                            value=TaskStatusState.value,
                            on_change=TaskStatusState.set_value,
                            name="status",
                        ),
                        # Hidden input for milestone_id
                        rx.input(
                            name="milestone_id",
                            value=milestone.id,  # Convert to string for input
                            class_name="hidden",
                        ),
                        rx.spacer(direction="column", spacing="3"),
                        rx.alert_dialog.action(
                            rx.button(
                                "Create Task",
                                color_scheme="blue",
                                type="submit",
                                margin_top="2rem",
                                class_name="w-full",
                                padding="1rem",
                            ),
                        ),
                        on_submit=Task_Form_State.submit,
                    ),
                    spacing="4",
                ),
            ),
            on_open_change=Task_Form_State.set_which_dialog_open(
                ""
            ),  # type:ignore
        ),
    )
