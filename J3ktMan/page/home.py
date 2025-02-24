import reflex as rx
from J3ktMan.component.project_card import project_card
from J3ktMan.component.base import base_page

def home() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.text("Home", size="7", weight="bold"),
            rx.grid(
                project_card(),
                columns="3",
                spacing="3",
                align="start",
                width="100%"
            )
        )
    )
