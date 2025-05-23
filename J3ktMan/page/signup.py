from J3ktMan.secret.clerk import PUBLISHABLE_KEY, SECRET_KEY

import reflex_clerk as clerk
import reflex as rx


def signup() -> rx.Component:
    return clerk.clerk_provider(
        rx.center(
            rx.vstack(
                clerk.sign_up(
                    path="/signup",
                    sign_in_url="/signin",
                    fallback_redirect_url="/home",
                ),
                align="center",
                spacing="7",
            ),
            height="100vh",
        ),
        publishable_key=PUBLISHABLE_KEY,
        secret_key=SECRET_KEY,
    )
