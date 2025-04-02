import reflex as rx
from reflex import State
from typing import Dict, List, Any


class TooltipState(rx.State):
    """State for the tooltip component."""

    visible: bool = False
    hovered_task_id: str = ""

    def show_tooltip(self, task_id: str) -> None:
        self.visible = True
        self.hovered_task_id = task_id

    def hide_tooltip(self) -> None:
        self.visible = False
        self.hovered_task_id = ""


def get_status_color(status: str):
    """Return color based on status."""
    if status == "DONE":
        return "#4caf50"
    elif status == "IN PROGRESS":
        return "#a881e6"
    else:
        return "#e0e0e0"


def month_header(month: str, width: str) -> rx.Component:
    """Month header box."""
    return rx.box(
        rx.text(month, font_size="14px", weight="bold"),
        min_width="300px",
        width=width,
        flex="0 0 auto",
        text_align="center",
        background_color="#303030",
        padding_y="0.5rem",
        border_right="1px solid #4d4d4d",
    )


def task_row(task: Dict[str, Any]) -> rx.Component:
    start_pos: float = task["start_position"]
    end_pos: float = task["end_position"]
    task_id: str = task["id"]

    # Calculate the width of the task bar
    width_percent = rx.cond(
        end_pos >= start_pos,
        end_pos - start_pos,
        0,
    )
    start_percent = start_pos

    # Positioning for start label
    start_label_left = rx.cond(
        start_pos < 5,  # If the start is near the left edge
        "0%",
        f"{start_percent}%",
    )
    start_label_transform = rx.cond(
        start_pos < 5,
        "translateX(0%)",  # No transform if near the left edge
        "translateX(-100%)",  # Move left so the right edge of the label aligns with the bar's start
    )

    # Positioning for end label
    end_label_left = rx.cond(
        end_pos > 95,  # If the end is near the right edge
        "100%",
        f"{end_pos}%",
    )
    end_label_transform = rx.cond(
        end_pos > 95,
        "translateX(-100%)",  # Move left so the label stays within bounds
        "translateX(0%)",  # No transform, so the left edge of the label aligns with the bar's end
    )

    # Align labels vertically with the bar
    label_top = "0px"  # Align with the top of the bar
    label_height = "20px"  # Match the bar height
    label_line_height = "20px"  # Center the text vertically within the label

    # For short tasks, adjust positioning to prevent overlap
    start_label_left_adjusted = rx.cond(
        (end_pos - start_pos) < 10,  # If the task is very short
        f"{start_percent}%",  # Keep it at the start
        start_label_left,
    )
    end_label_left_adjusted = rx.cond(
        (end_pos - start_pos) < 10,
        f"{end_pos}%",  # Keep it at the end
        end_label_left,
    )

    # Ensure labels are aligned properly with the bar's edges
    start_label_text_align = rx.cond(
        start_pos < 5,
        "left",  # Align left if near the left edge
        "right",  # Align right so the label's right edge is flush with the bar's start
    )
    end_label_text_align = rx.cond(
        end_pos > 95,
        "right",  # Align right if near the right edge
        "left",  # Align left so the label's left edge is flush with the bar's end
    )

    return rx.hstack(
        rx.box(
            rx.box(
                # Start date label
                rx.text(
                    task["start_date"],
                    color="#eee",
                    font_size="12px",
                    font_weight="medium",
                    padding="0.25rem 0.5rem",
                    background_color="#333",
                    border_radius="3px",
                    position="absolute",
                    top=label_top,  # Align with the top of the bar
                    height=label_height,  # Match the bar height
                    line_height=label_line_height,  # Center text vertically
                    left=start_label_left_adjusted,
                    transform=start_label_transform,
                    text_align=start_label_text_align,
                    white_space="nowrap",
                    display=rx.cond(
                        (TooltipState.visible)
                        & (TooltipState.hovered_task_id == task_id),
                        "block",
                        "none",
                    ),
                ),
                # End date label
                rx.text(
                    task["end_date"],
                    color="#eee",
                    font_size="12px",
                    font_weight="medium",
                    padding="0.25rem 0.5rem",
                    background_color="#333",
                    border_radius="3px",
                    position="absolute",
                    top=label_top,  # Align with the top of the bar
                    height=label_height,  # Match the bar height
                    line_height=label_line_height,  # Center text vertically
                    left=end_label_left_adjusted,
                    transform=end_label_transform,
                    text_align=end_label_text_align,
                    white_space="nowrap",
                    display=rx.cond(
                        (TooltipState.visible)
                        & (TooltipState.hovered_task_id == task_id),
                        "block",
                        "none",
                    ),
                ),
                on_mouse_over=lambda: TooltipState.show_tooltip(
                    task_id
                ),  # type:ignore
                on_mouse_out=TooltipState.hide_tooltip,  # type:ignore
                position="absolute",
                left=f"{start_percent}%",
                height="20px",
                width=f"{width_percent}%",
                background_color="#5b279c",
                border_radius="3px",
            ),
            position="relative",
            height="40px",
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
