import reflex as rx
from J3ktMan.component.base import base_page
from J3ktMan.component.Dashboard.bar_chart import bar_chart
from J3ktMan.component.Dashboard.pie_chart import pie_chart
from J3ktMan.component.Dashboard.dashboard_card import dashboard_card


def dashboard() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.text("Dashboard", size="7", weight="bold"),
            rx.hstack(
                rx.box(
                    dashboard_card(name="Completed Projects", icon="circle-check"),
                    width="33%",
                ),
                rx.box(
                    dashboard_card(name="Task created", icon="book-check"),
                    width="33%",
                ),
                rx.box(
                    dashboard_card(name="Task due", icon="calendar-clock"),
                    width="33%",
                ),
                width="100%",
            ),
            rx.spacer(),
            rx.hstack(
                rx.card(
                    rx.text("Priority Breakdown", size="5", weight="bold"),
                    rx.box(
                        bar_chart(),
                    ),
                    padding="4",
                    width="100%",
                    height="300px",
                ),
                rx.card(
                    rx.text("Status overview", size="5", weight="bold"),
                    rx.box(
                        pie_chart(),
                    ),
                    padding="4",
                    height="300px",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            width="100%",
            spacing="4",
        )
    )
