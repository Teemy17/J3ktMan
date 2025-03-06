import reflex as rx


def dashboard_card(name: str, icon: str, width: str = "100%") -> rx.Component:
    return rx.flex(
        rx.card(
            rx.icon(icon, color="primary"),
            rx.text(name, size="4", weight="bold"),
            size="4",
            width="100%",
        ),
        spacing="2",
        align_items="flex-start",
        flex_wrap="wrap",
        width=width,
    )
