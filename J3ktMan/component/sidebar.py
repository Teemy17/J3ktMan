import reflex as rx

def sidebar_item(
    text: str, icon: str, href: str
) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon),
            rx.text(text, size="4"),
            width="100%",
            padding_x="0.5rem",
            padding_y="0.75rem",
            align="center",
            class_name="hover:bg-gray-900",
            # style={
            #     "_hover": {
            #         "bg": rx.color("accent", 4),
            #         "color": rx.color("accent", 11),
            #     },
            #     "border-radius": "0.5em",
            # },
        ),
        href=href,
        underline="none",
        weight="medium",
        width="100%",
    )


def sidebar_items() -> rx.Component:
    return rx.vstack(
        sidebar_item("Home", "home", "/#"),
        sidebar_item("Dashboard", "layout-dashboard", "/#"),
        sidebar_item("Kanban Board", "kanban", "/#"),
        sidebar_item("Timeline", "chart-gantt", "/#"),
        sidebar_item("Members", "users", "/#"),
        spacing="1",
        width="100%",
    )


def sidebar() -> rx.Component:
       return rx.box(
        rx.desktop_only(
            rx.vstack(
                sidebar_items(),
                spacing="5",
                padding_x="1em",
                padding_y="1.5em",
                # bg=rx.color("accent", 1),
                align="start",
                height="100vh",
                min_height="100%",
                width="16em",
                class_name="shadow-lg dark:bg-zinc-900",
                border_right="2px solid rgb(38, 39, 43)",
            ),
        ), 
        rx.mobile_and_tablet(
            rx.drawer.root(
                rx.drawer.trigger(
                    rx.icon("align-justify", size=30)
                ),
                rx.drawer.overlay(z_index="5"),
                rx.drawer.portal(
                    rx.drawer.content(
                        rx.vstack(
                            rx.box(
                                rx.drawer.close(
                                    rx.icon("x", size=30)
                                ),
                                width="100%",
                            ),
                            sidebar_items(),
                            spacing="5",
                            width="100%",
                        ),
                        top="auto",
                        right="auto",
                        height="100%",
                        width="20em",
                        padding="1.5em",
                        # bg=rx.color("accent", 2),
                    ),
                    width="100%",
                ),
                direction="left",
            ),
            # padding="1em",
        ),
        # border_right="1px solid rgb(230, 230, 230)",
    )