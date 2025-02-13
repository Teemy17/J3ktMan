import reflex as rx
import reflex_clerk as clerk


from J3ktMan.component.protected import protected_page


@protected_page
def index() -> rx.Component:
    return rx.vstack(
        rx.text(f"Hello {clerk.ClerkState.user.username}"),  # type: ignore
        clerk.sign_out_button(rx.button("Sign Out")),
        rx.text("You are signed in!"),
    )
