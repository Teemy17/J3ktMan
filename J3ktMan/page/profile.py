import reflex_clerk as clerk
import reflex as rx
from J3ktMan.component.base import base_page
from J3ktMan.secret.clerk import PUBLISHABLE_KEY, SECRET_KEY


@rx.page(route="/profile")
def profile() -> rx.Component:
    profile_content = rx.center(
        rx.vstack(
            clerk.user_profile(),
            align="center",
            spacing="7",
        ),
        width="100%",
        height="100%",
    )

    return clerk.clerk_provider(
        base_page(profile_content),
        publishable_key=PUBLISHABLE_KEY,
        secret_key=SECRET_KEY,
    )
