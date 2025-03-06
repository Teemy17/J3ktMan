import reflex as rx
from J3ktMan.component.project_card import project_card
from J3ktMan.component.base import base_page
from J3ktMan.component.create_project_dialog import create_project_dialog
from J3ktMan.state.home_state import HomeState


def home() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.text("Home", size="7", weight="bold"),
            create_project_dialog(rx.button("Create Project")),
            rx.grid(
                rx.foreach(
                    HomeState.get_user_projects,  # type: ignore
                    lambda project: project_card(
                        name=project.name,
                        description=f"Created at: {project.created_at}",
                        comments=0,
                        files=0,
                    ),
                ),
                columns="3",
                spacing="6",
                align="start",
                width="100%",
            ),
            width="100%",
        )
    )
