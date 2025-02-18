import reflex as rx
import reflex_clerk as clerk


from J3ktMan.component.create_project_dialog import create_project_dialog
from J3ktMan.component.invite_member_dialog import invite_member_dialog
from J3ktMan.component.protected import protected_page


@protected_page
def index() -> rx.Component:
    return rx.vstack(
        rx.text(f"Hello {clerk.ClerkState.user.username}"),  # type: ignore
        clerk.sign_out_button(rx.button("Sign Out")),
        rx.text("You are signed in!"),
        invite_member_dialog(rx.button("Invite Member"), 1),
        create_project_dialog(
            rx.button("Create Project"),
        ),
        rx.button(on_click=rx.toggle_color_mode),
    )
