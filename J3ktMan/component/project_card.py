import reflex as rx

def project_card(name: str, description: str, comments: int, files: int) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading(name, size="3"),
            rx.text(description, size="2", color="gray"),
            rx.hstack(
                rx.hstack(
                    rx.icon("message-circle"),
                    rx.text(f"{comments} comments", size="1"),
                    rx.icon("file"),
                    rx.text(f"{files} files", size="1"),
                    spacing="2",
                ),
                align="center",
            ),
            spacing="4",
            align="start",
        ),
        padding="4",
        border_radius="lg",
        shadow="md",
    )
