import reflex as rx
import reflex_clerk as clerk


def index() -> rx.Component:
    return rx.vstack("test", clerk.clerk_provider(clerk.sign_out_button()))
