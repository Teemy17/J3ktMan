import reflex as rx


def month_header(month) -> rx.Component:
    """Month header box."""
    return rx.box(
        rx.text(month, font_size="14px", weight="bold"),
        flex="1",
        text_align="center",
        background_color="#f0f2f5",
        padding_y="0.5rem",
    )


def task_row(task) -> rx.Component:
    """Task row with the timeline bar."""
    return rx.hstack(
        # Task info
        rx.hstack(
            rx.icon("square", color="#a881e6"),
            rx.text(f"{task['name']}", color="#666", font_size="14px"),
            spacing="2",
            align_items="center",
            width="25%",
        ),
        # Task timeline bar
        rx.box(
            rx.box(
                position="absolute",
                left=f"{task['start_position']}%",
                height="20px",
                width=f"{task['end_position']}%",
                background_color="#a881e6",
                border_radius="3px",
            ),
            position="relative",
            height="30px",
            width="75%",
        ),
        width="100%",
        padding_y="0.5rem",
        border_bottom="1px solid #eee",
    )
