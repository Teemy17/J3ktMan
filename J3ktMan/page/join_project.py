from J3ktMan.component.protected import protected_page

from reflex_clerk import ClerkState
from reflex.event import EventSpec

import reflex as rx

from J3ktMan.crud.project import (
    get_project_from_invitation_code,
    reedem_invitation_code,
)


class InvalidCode(rx.Base): ...


class InvitedPorject(rx.Base):
    id: int
    name: str
    code: str


class State(rx.State):
    project: InvitedPorject | InvalidCode | None = None

    @rx.var(cache=False)
    def is_loading(self) -> bool:
        return self.project is None

    @rx.var(cache=False)
    def invalid_code(self) -> bool:
        return isinstance(self.project, InvalidCode)

    @rx.event
    async def on_accept(self) -> list[EventSpec] | None:
        clerk_state: ClerkState = await self.get_state(ClerkState)

        if clerk_state.user_id is None:
            return rx.toast.error(
                "Please sign in to join the project.", position="top-center"
            )

        # should not happen
        if not isinstance(self.project, InvitedPorject):
            return None

        success = reedem_invitation_code(
            self.project.code, clerk_state.user_id
        )

        if success:
            # TODO: redirect to the project page or something
            return [rx.redirect("/")]
        else:
            return rx.toast.error(
                "Can't join the project; the invitation code might've been expired"
            )

    @rx.event
    def back(self) -> EventSpec:
        return rx.redirect("/")

    @rx.event
    def on_load(self) -> None:
        self.project = InvalidCode()
        code: str | None = self.router.page.params.get("code", None)

        # somehow the code is missing, which should not happen
        if code is None:
            return

        project = get_project_from_invitation_code(code)

        if project is None:
            self.project = InvalidCode()
            return

        self.project = InvitedPorject(
            id=project.id, name=project.name, code=code
        )

        # TODO: add some check whether the user has already join this project


@rx.page(route="/project/join/[code]", on_load=State.on_load)
@protected_page
def join_project() -> rx.Component:
    return rx.center(
        rx.skeleton(
            rx.card(
                rx.vstack(
                    rx.badge(
                        rx.cond(
                            State.invalid_code,
                            rx.icon("triangle-alert", size=60),
                            rx.icon("circle-check", size=60),
                        ),
                        color_scheme=rx.cond(
                            State.invalid_code, "red", "mint"
                        ),
                        padding="0.65rem",
                        class_name="rounded-xl text-2xl shadow-md",
                    ),
                    rx.cond(
                        State.invalid_code,
                        rx.vstack(
                            rx.heading("Invalid Code", size="4"),
                            rx.text(
                                "Your code might have been expired.", size="2"
                            ),
                            align="center",
                            margin_y="1rem",
                        ),
                        rx.vstack(
                            rx.text("You've been invited to join", size="2"),
                            rx.heading(
                                State.project.name,  # type:ignore
                                size="4",
                            ),
                            align="center",
                            margin_y="1rem",
                        ),
                    ),
                    rx.cond(
                        State.invalid_code,
                        rx.button(
                            "Back to Home",
                            width="100%",
                            class_name="""
                                shadow-md bg-transparent text-slate-500 border 
                                rounded-md border-solid border-slate-100
                                hover:bg-slate-100 hover:text-slate-700 
                                dark:text-slate-200 dark:border-slate-600  
                                dark:hover:bg-slate-600 dark:hover:text-slate-200
                            """,
                            on_click=State.back,
                        ),
                        rx.fragment(
                            rx.button(
                                "Accept",
                                width="100%",
                                class_name="shadow-md",
                                on_click=State.on_accept,
                            ),
                            rx.button(
                                "Decline",
                                width="100%",
                                class_name="""
                                    shadow-md bg-transparent text-slate-500 
                                    border rounded-md border-solid 
                                    border-slate-100 hover:bg-slate-100 
                                    hover:text-slate-700 dark:text-slate-200
                                    dark:border-slate-600  
                                    dark:hover:bg-slate-600 
                                    dark:hover:text-slate-200
                                """,
                                on_click=State.back,
                            ),
                        ),
                    ),
                    padding_y="1rem",
                    padding_x="1rem",
                    align="center",
                )
            ),
            loading=State.is_loading,
        ),
        height="100vh",
    )
