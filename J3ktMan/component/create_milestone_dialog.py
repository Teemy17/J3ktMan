from reflex.event import EventSpec
import reflex as rx

from J3ktMan.model.tasks import Milestone
from J3ktMan.crud.tasks import (
    ExistingMilestoneNameError,
    MilestoneCreate,
    create_milestone,
)


class State(rx.State):
    _last_created_milestone: Milestone | None = None
    _project_id: int | None = None

    @rx.var
    def last_created_milestone(self) -> Milestone | None:
        """
        Obtains the milestone that was created by this dialog since the last
        open and submission
        """

        return self._last_created_milestone

    @rx.event
    def submit(self, form) -> list[EventSpec] | None:
        name = str(form["name"])
        description = str(form["description"])

        if self._project_id is None:
            print(self._project_id)
            return

        try:
            milestone = create_milestone(
                MilestoneCreate(
                    name=name,
                    description=description,
                    parent_project_id=self._project_id,
                )
            )

            self._last_created_milestone = milestone

            return [
                rx.toast.success(
                    f"Milestone {name} has been created",
                    position="top-center",
                ),
            ]

        except ExistingMilestoneNameError:
            self._last_created_milestone = None

            return [
                rx.toast.error(
                    f"Milestone {name} already exists",
                    position="top-center",
                ),
            ]

    @rx.event
    def on_open_change(self, project_id: int, open: bool):
        if open:
            self.reset()

        self._last_created_milestone = None
        self._project_id = project_id


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


def create_milestone_dialog(
    trigger: rx.Component,
    project_id: int,
    on_create_milestone=None,
) -> rx.Component:
    """
    NOTE on how to use `on_create_milestone`: this event handler will be invoked
    upon the form submission in the dialog regardless whether or not it succeeds
    or not. The event handler should take no arguments. To inspect the milestone
    that has been created, you should retrieve the
    `State.last_created_milestone`, which can be `None | Milestone` depends on
    whether the milestone was created successfully or not. It should look
    something like this

    ```
    class MyState(rx.State):
        @rx.event
        async def event(self);
            milestone_diag_state = await self.get_state(State)

            # inspect the last created milestone
            milestone_diag_state.last_created_milestone

    def component() -> rx.Component
        create_milestone_dialog(
            trigger,
            project_id,
            MyState.event
        )
    ```
    """
    on_submit = [State.submit]

    if on_create_milestone is not None:
        if isinstance(on_create_milestone, list):
            for x in on_create_milestone:
                on_submit.append(x)
        else:
            on_submit.append(on_create_milestone)

    return rx.dialog.root(
        rx.dialog.trigger(trigger),
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
                on_submit=on_submit,  # type: ignore
            ),
            width="fit-content",
            min_width="20rem",
        ),
        on_open_change=lambda e: State.on_open_change(project_id, e),
    )
