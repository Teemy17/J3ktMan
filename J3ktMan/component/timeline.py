import reflex as rx
from typing import Dict, List, Any


def get_status_color(status):
    """Return color based on status."""
    if status == "DONE":
        return "#4caf50"
    elif status == "IN PROGRESS":
        return "#a881e6"
    else:
        return "#e0e0e0"


def month_header(month) -> rx.Component:
    """Month header box."""
    return rx.box(
        rx.text(month, font_size="14px", weight="bold"),
        flex="1",
        text_align="center",
        background_color="#303030",
        padding_y="0.5rem",
    )


def task_row(task) -> rx.Component:
    """Task row with the timeline bar."""
    return rx.hstack(
        # Task timeline bar
        rx.box(
            rx.box(
                position="absolute",
                left=f"{task['start_position']}%",
                height="20px",
                width=f"{task['end_position']}%",
                background_color="#5b279c",
                border_radius="3px",
            ),
            position="relative",
            height="100%",
            width="100%",
        ),
        width="100%",
        padding_y="0.5rem",
        border_bottom="1px solid #4d4d4d",
        height="40px",  # Fixed height to match timeline rows
    )


def task_name(task: Dict[str, Any]) -> rx.Component:
    """Task name box."""
    status_color = get_status_color(str(task["status"]))

    return rx.box(
        rx.hstack(
            rx.box(
                width="12px",
                height="12px",
                background_color=status_color,
                border_radius="2px",
            ),
            rx.text(
                task["name"],
                color="#eee",
                font_size="14px",
                font_weight="medium",
            ),
            spacing="2",
            align_items="center",
        ),
        width="100%",
        padding="0.5rem",
        border_bottom="1px solid #4d4d4d",
        height="40px",  # Fixed height to match timeline rows
    )
