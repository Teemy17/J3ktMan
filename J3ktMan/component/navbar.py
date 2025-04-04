import reflex as rx
import reflex_clerk as clerk
from reflex_clerk.lib.appearance import Appearance


def logo() -> rx.Component:
    return rx.hstack(
        rx.text(
            "J3ktMan",
            size="7",
            weight="bold",
            on_click=rx.redirect("/home"),
            style={"cursor": "pointer"},  # type: ignore
        ),
    )


def notification_icons() -> rx.Component:
    return rx.hstack(
        rx.icon_button(
            rx.icon("calendar"),
            variant="ghost",
            aria_label="Calendar",
        ),
        rx.icon_button(
            rx.icon("message-circle-question"),
            variant="ghost",
            aria_label="Messages",
        ),
        rx.icon_button(
            rx.icon("bell"),
            variant="ghost",
            aria_label="Notifications",
        ),
        rx.color_mode_cond(
            light=rx.icon_button(
                rx.icon("moon"),
                variant="ghost",
                aria_label="Dark mode",
                on_click=rx.toggle_color_mode,
            ),
            dark=rx.icon_button(
                rx.icon("sun"),
                variant="ghost",
                aria_label="Light mode",
                on_click=rx.toggle_color_mode,
            ),
        ),
        spacing="7",
    )


def user_profile() -> rx.Component:
    return (
        rx.hstack(
            clerk.user_button(),
            rx.vstack(
                rx.text(
                    clerk.ClerkState.user.username,  # type: ignore
                    size="4",
                    weight="medium",
                ),
                align_items="start",
                justify="center",
                spacing="0",
                width="100%",
            ),
            rx.icon("chevron-down", color="gray"),
            padding="4px",
            border_radius="8px",
        ),
    )


def navbar() -> rx.Component:
    return rx.box(
        rx.desktop_only(
            rx.hstack(
                logo(),
                rx.spacer(),
                notification_icons(),
                user_profile(),
                width="100%",
                padding="1em",
                justify="between",
                align_items="center",
                spacing="9",
            ),
        ),
        rx.mobile_and_tablet(
            rx.hstack(
                rx.spacer(),
                notification_icons(),
                user_profile(),
                width="100%",
                padding="1em",
                justify="between",
                align_items="center",
            ),
        ),
        border_bottom=rx.color_mode_cond(
            dark="2px solid rgb(38, 39, 43)", light="2px solid #E2E8F0"
        ),
        width="100%",
    )
