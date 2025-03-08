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


def month_header(month: str) -> rx.Component:
    """Month header box."""
    return rx.box(
        rx.text(month, font_size="14px", weight="bold"),
        min_width="300px",
        flex="0 0 auto",
        text_align="center",
        background_color="#303030",
        padding_y="0.5rem",
        border_right="1px solid #4d4d4d",
    )


def task_row(task: Dict[str, Any]) -> rx.Component:
    start_pos = task["start_position"]
    end_pos = task["end_position"]
    width_percent = rx.cond(
        end_pos >= start_pos,
        end_pos - start_pos,
        0,  # Default to 0 if subtraction is invalid
    )
    start_percent = start_pos

    print("Task:", task)
    print("Width percent (reactive):", width_percent)
    print("Start percent (reactive):", start_percent)

    return rx.hstack(
        rx.box(
            rx.box(
                position="absolute",
                left=f"{start_percent}%",
                height="20px",
                width=f"{width_percent}%",
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
        height="40px",
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
