import reflex as rx
from J3ktMan.component.base import base_page
from J3ktMan.component.Dashboard.bar_chart import bar_chart
from J3ktMan.component.Dashboard.pie_chart import pie_chart

def dashboard() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.text("Dashboard", size="7", weight="bold"),
            rx.grid(
                rx.card(
                    rx.box(
                        bar_chart(),
                        width="100%",
                        height="250px",
                    ),
                    padding="4",
                    width="100%",
                ),
                rx.card(
                    rx.box(
                        pie_chart(),
                    ),
                    padding="4",
                    height="300px",
                    width="100%",
                ),
                template_columns="repeat(auto-fit, minmax(350px, 1fr))",
                gap="4",
                width="100%",
                spacing_y="5",
            ),
            width="100%",
            spacing="4",
        )
    )
