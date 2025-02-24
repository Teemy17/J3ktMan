import reflex as rx

def project_card() -> rx.Component:
    return rx.card(
        rx.flex(
            rx.text("Project Name", size="5", weight="bold"),
            rx.icon("move-vertical", color="gray"),
            spacing="2",
        ),
        rx.text("Project Description", size="3", color="gray"),
    )
