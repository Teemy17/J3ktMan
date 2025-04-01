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
        _hover=rx.color_mode_cond(
            light={
                "background": "#F7FAFC",
                "transform": "translateY(-2px)",
                "box_shadow": "0 4px 6px rgba(0, 0, 0, 0.1)"
            },
            dark={
                "background": "gray.700",
                "transform": "translateY(-2px)",
                "box_shadow": "0 4px 6px rgba(0, 0, 0, 0.4)"
            }
        ),
        on_click=rx.redirect("/project/[[...slug]]")
    )
