from reflex.event import EventSpec
from reflex_clerk import ClerkState
from typing import Any
import reflex as rx

from J3ktMan.crud.project import (
    ExistingProjectNameError,
    ProjectCreate,
    TooShortProjectNameError,
    create_project,
)
from J3ktMan.state.home_state import HomeState

class State(rx.State):
    @rx.event
    async def submit(self, form: dict[str, Any]) -> EventSpec | None:
        clerk_state = await self.get_state(ClerkState)

        # should not happen if the page is protected
        if clerk_state.user_id is None:
            return rx.toast.error(
                "Please sign in to create a project.", position="top-center"
            )

        project_name = str(form["name"])

        try:
            create_project(
                ProjectCreate(user_id=clerk_state.user_id, name=project_name)
            )

            # Refresh the projects list
            home_state = await self.get_state(HomeState)
            home_state.refresh_projects()

            return rx.toast.info(
                f"Project '{project_name}' created successfully."
            )

        except TooShortProjectNameError:
            return rx.toast.error(
                "Project name should be at least 4 characters.",
                position="top-center",
            )

        except ExistingProjectNameError:
            return rx.toast.error(
                "Project with the same name already exists.",
                position="top-center",
            )


def form_field(
    label: str, placeholder: str, type: str, name: str
) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.form.label(label),
            rx.form.control(
                rx.input(placeholder=placeholder, type=type),
                as_child=True,
            ),
            direction="column",
            spacing="1",
        ),
        name=name,
        width="100%",
    )


def create_project_dialog(trigger: rx.Component) -> rx.Component:
    """
    A component that renders a dialog to create a new project.

    ```python
    create_project_dialog(rx.button("Create Project"))
    ```
    """
    return rx.dialog.root(
        rx.dialog.trigger(trigger),
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.badge(
                        rx.icon(tag="folder-plus"),
                        color_scheme="mint",
                        radius="full",
                        padding="0.65rem",
                    ),
                    rx.vstack(
                        rx.heading("Create Project", size="4"),
                        rx.text(
                            "Fill the form to get started with a new project.",
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
                    form_field("Name", "Enter project name", "text", "name"),
                    rx.dialog.close(
                        rx.button(
                            "Create",
                            type="submit",
                            margin_top="1rem",
                        )
                    ),
                    direction="column",
                ),
                on_submit=State.submit,
            ),
            width="fit-content",
            min_width="20rem",
        ),
    )
