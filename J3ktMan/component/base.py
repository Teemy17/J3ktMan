import reflex as rx
from .navbar import navbar
from .sidebar import sidebar

def base_layout_component(child, *args, **kwargs) -> rx.Component:
    """
    A base layout component that wraps a child component in a layout with a navbar and sidebar.
    """
    return rx.box(
        rx.vstack(
            navbar(),
            rx.hstack(
                sidebar(),
                rx.box(
                    child,
                    padding="1em",
                    flex="1",
                    width="100%",
                    min_height="calc(100vh - 73px)",  
                    overflow_y="auto",
                ),
                spacing="0",
                align="stretch",
                width="100%",
                height="calc(100vh - 73px)",  
                overflow="hidden",
            ),
            spacing="0",
            width="100%",
            height="100vh",
            overflow="hidden",
        ),
        width="100%",
        height="100vh",
    )

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    return base_layout_component(child, *args, **kwargs)
