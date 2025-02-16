from J3ktMan.crud.project import get_invitation_code

from reflex_clerk import ClerkState
import reflex as rx


class InviteMemberDialog(rx.ComponentState):
    link: str | None

    @rx.var
    def is_loading(self) -> bool:
        return self.link is None

    @rx.event
    async def on_open(self, value: bool, project_id: int):
        if not value or self.link is not None:
            return

        clerk_state = await self.get_state(ClerkState)

        if clerk_state.user_id is None:
            return rx.toast.error(
                "Please sign in to invite a member.", position="top-center"
            )

        # let's do for 10 minutes and no redeem limit. we can add options to
        # change this later
        code = get_invitation_code(
            clerk_state.user_id,
            project_id,
            600,
            redeem_limit=None,
        )

        self.link = self.router.page.host + f"/project/join/{code}"

    @rx.event
    async def on_copy_link(self):
        if self.link is None:
            return

        return [
            rx.set_clipboard(self.link),
            rx.toast.info(
                "Link copied to clipboard; the link will expire in 10 minutes.",
            ),
        ]

    @classmethod
    def get_component(
        cls, trigger: rx.Component, project_id: int, **_
    ) -> rx.Component:
        return rx.dialog.root(
            rx.dialog.trigger(trigger),
            rx.dialog.content(
                rx.vstack(
                    rx.hstack(
                        rx.badge(
                            rx.icon(tag="external-link"),
                            color_scheme="mint",
                            radius="full",
                            padding="0.65rem",
                        ),
                        rx.vstack(
                            rx.heading("Invite Member", size="4"),
                            rx.text(
                                "Share the link below to invite a member to your project.",
                                size="2",
                            ),
                            spacing="1",
                            align_items="start",
                        ),
                        align_items="center",
                        padding_bottom="1rem",
                    ),
                ),
                rx.form.root(
                    rx.flex(
                        rx.skeleton(
                            rx.input(
                                rx.input.slot(
                                    rx.icon(
                                        "copy",
                                        class_name="p-1",
                                    ),
                                ),
                                placeholder=cls.link,
                                type="text",
                                size="2",
                                disabled=True,
                                read_only=True,
                                width="100%",
                            ),
                            loading=cls.is_loading,
                        ),
                        rx.dialog.close(
                            rx.button(
                                "Copy Link",
                                type="submit",
                                width="100%",
                                margin_top="1rem",
                                on_click=cls.on_copy_link,
                            ),
                        ),
                        direction="column",
                    ),
                ),
                width="fit-content",
                min_width="20rem",
            ),
            on_open_change=lambda open: cls.on_open(open, project_id),
        )


invite_member_dialog = InviteMemberDialog.create
