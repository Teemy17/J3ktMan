import reflex as rx

def logo() -> rx.Component:
    return rx.hstack(
        rx.text("J3ktMan", size="7", weight="bold"),
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
        spacing="7",
    )

def user_profile() -> rx.Component:
    return rx.menu.root(
        rx.menu.trigger(
            rx.hstack(
                rx.avatar(
                    name="Anima Agrawal",
                    size="3",
                    src="https://via.placeholder.com/40",
                    border_radius="full",
                ),
                rx.vstack(
                    rx.text("Ricardo Milos", size="3", weight="medium"),
                    rx.text("Brazil", size="2", color="gray"),
                    align_items="start",
                    spacing="0",
                ),
                rx.icon("chevron-down", color="gray"),
                padding="4px",
                border_radius="8px",
                _hover={"background": "grey"},
            )
        ),
        rx.menu.content(
            rx.menu.item("Profile"),
            rx.menu.item("Settings"),
            rx.menu.separator(),
            rx.menu.item("Log out"),
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
                rx.icon_button(
                    rx.icon("search"),
                    variant="ghost",
                ),
                rx.spacer(),
                notification_icons(),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.avatar(
                            name="Anima Agrawal",
                            size="3",
                            border_radius="full",
                        ),
                    ),
                    rx.menu.content(
                        rx.menu.item("Profile"),
                        rx.menu.item("Settings"),
                        rx.menu.separator(),
                        rx.menu.item("Log out"),
                    ),
                ),
                width="100%",
                padding="1em",
                justify="between",
                align_items="center",
            ),
        ),
        border_bottom="1px solid rgb(230, 230, 230)",
        # background="white",
        width="100%",
    )