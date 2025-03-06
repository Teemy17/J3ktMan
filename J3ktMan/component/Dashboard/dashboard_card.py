import reflex as rx


def dashboard_card(name: str) -> rx.Component:
    return rx.flex(
        rx.card(
            rx.text(name, size="4", weight="bold"),
            size="4",
        ),
        spacing="2",
        align_items="flex-start",
        flex_wrap="wrap",
    )
