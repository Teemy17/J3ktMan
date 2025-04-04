import reflex as rx
from reflex.event import EventSpec
from typing import Any, Dict, List
from J3ktMan.utils import date_to_epoch
from J3ktMan.state.project import State as ProjectState
from J3ktMan.model.tasks import Priority


class DateError(Exception):
    pass


class TaskFormState(rx.State):
    milestone_id: int | None = None

    def check_date_validity(self) -> bool:
        """
        Check if the start date is before the end date.
        """
        if self.start_date >= self.end_date:
            return False
        return True

    @rx.var(cache=True)
    async def milestone_names(self) -> list[str]:
        """
        Get the list of milestones from the project state.
        """
        state = await self.get_state(ProjectState)
        return [milestone.name for milestone in state.milestones]

    @rx.var(cache=True)
    async def status_names(self) -> list[str]:
        state = await self.get_state(ProjectState)
        return [status.name for status in state.statuses]

    @rx.event
    async def submit(self, form: Dict[str, Any]) -> list[EventSpec] | None:
        """
        Handle form submission.
        """
        if self.milestone_id is None:
            return

        state = await self.get_state(ProjectState)

        name: str = form["name"]
        status_str: str = form["status"]
        priority_str: str = form["priority"]

        missing_fields = []

        if len(name) == 0:
            missing_fields.append('"name"')

        if len(priority_str) == 0:
            missing_fields.append('"priority"')

        if len(status_str) == 0:
            missing_fields.append('"status"')

        if len(missing_fields) > 0:
            return rx.toast.error(
                "Please fill in all required fields, including: "
                + ", ".join(missing_fields),
                position="top-center",
            )

        description: str = form["description"]

        priority = Priority(priority_str.upper())

        start_date_str: str = form["start_date"]
        start_date = (
            date_to_epoch(start_date_str) if len(start_date_str) > 0 else None
        )

        end_date_str: str = form["end_date"]
        end_date = (
            date_to_epoch(end_date_str) if len(end_date_str) > 0 else None
        )

        status_id: int | None = None
        for status in state.statuses:
            if status.name == status_str:
                status_id = status.id
                break

        assert status_id is not None, "Status ID not found"

        created_task = state.create_task(
            name,
            description,
            priority,
            status_id,
            self.milestone_id,
            start_date,
            end_date,
        )

        return created_task

    @rx.event
    def set_which_dialog_open(self, milestone_id: int | None) -> None:
        """
        Set the milestone ID for the task form.
        """
        self.milestone_id = milestone_id


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


def form_field(
    child: rx.Component,
    label: str,
    name: str,
    class_name: str | None = None,
) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.form.label(label),
            child,
            direction="column",
            spacing="1",
        ),
        name=name,
        class_name=class_name,
    )


def create_task_dialog(milestone) -> rx.Component:
    """
    Dialog popup for creating a new task.
    """

    return (
        rx.dialog.root(
            rx.dialog.trigger(
                rx.button(
                    rx.icon(tag="plus", size=14),
                    size="1",
                    variant="ghost",
                    color_scheme="gray",
                    class_name="mx-1",
                ),
            ),
            rx.dialog.content(
                rx.vstack(
                    rx.hstack(
                        rx.badge(
                            rx.icon(tag="list-todo"),
                            radius="full",
                            padding="0.65rem",
                        ),
                        rx.vstack(
                            rx.heading("Create Task", size="4"),
                            rx.text(
                                f'Create new Task under milestone "{milestone.name}"',
                                size="2",
                            ),
                            spacing="1",
                            align_items="start",
                        ),
                        align_items="center",
                        padding_bottom="1rem",
                    ),
                    rx.form.root(
                        rx.flex(
                            form_field(
                                rx.input(
                                    name="name",
                                    placeholder="Enter task name",
                                    type="text",
                                ),
                                "Task Name",
                                "name",
                            ),
                            form_field(
                                rx.text_area(
                                    name="description",
                                    placeholder="Enter task name",
                                    type="text",
                                ),
                                "Description",
                                "description",
                            ),
                            rx.flex(
                                form_field(
                                    rx.select(
                                        TaskFormState.status_names,
                                        placeholder="Select Status",
                                        name="status",
                                    ),
                                    "Status",
                                    "status",
                                    class_name="flex-1",
                                ),
                                form_field(
                                    rx.select(
                                        ["Low", "Medium", "High"],
                                        placeholder="Select Priority",
                                        name="priority",
                                    ),
                                    "Priority",
                                    "priority",
                                    class_name="flex-1",
                                ),
                                direction="row",
                                class_name="gap-4 w-full",
                            ),
                            rx.flex(
                                form_field(
                                    rx.input(
                                        name="start_date",
                                        placeholder="Enter start date",
                                        type="date",
                                    ),
                                    "Start Date",
                                    "start_date",
                                    class_name="flex-1",
                                ),
                                form_field(
                                    rx.input(
                                        name="end_date",
                                        placeholder="Enter end date",
                                        type="date",
                                    ),
                                    "End Date",
                                    "end_date",
                                    class_name="flex-1",
                                ),
                                direction="row",
                                class_name="gap-4 w-full",
                            ),
                            direction="column",
                        ),
                        rx.spacer(direction="column", spacing="3"),
                        rx.dialog.close(
                            rx.button(
                                "Create Task",
                                color_scheme="blue",
                                type="submit",
                                margin_top="2rem",
                                class_name="w-full",
                                padding="1rem",
                            ),
                        ),
                        on_submit=TaskFormState.submit,
                    ),
                    spacing="4",
                ),
            ),
            on_open_change=TaskFormState.set_which_dialog_open(
                milestone.id
            ),  # type:ignore
        ),
    )
