from J3ktMan.secret.clerk import PUBLISHABLE_KEY, SECRET_KEY

import reflex_clerk as clerk
import reflex as rx


def signin() -> rx.Component:
    return clerk.clerk_provider(
        rx.center(
            rx.vstack(
                clerk.sign_in(
                    path="/signin",
                    sign_up_url="/signup",
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
