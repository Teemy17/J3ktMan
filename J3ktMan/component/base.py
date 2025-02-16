import reflex as rx
from .navbar import navbar

def base_layout_component(child, *args, **kwargs) -> rx.Component:
    return rx.fragment(
        rx.box(
            navbar(),
            rx.box (
                child,
                padding="1em",
                width="100%",
            ),
        )
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    return base_layout_component(child, *args, **kwargs)