import reflex as rx


class DrawerState(rx.State):
    is_open: bool = False
    is_desktop_expanded: bool = True

    @rx.event
    def toggle(self):
        self.is_open = not self.is_open

    @rx.event
    def toggle_desktop(self):
        self.is_desktop_expanded = not self.is_desktop_expanded


class SidebarState(rx.State):
    @rx.var
    def current_project_id(self) -> str | None:
        """Get the current project ID from the URL path if available."""
        try:
            # Check if we're on a project page
            path = self.router.page.path
            if "/project/" in path:
                # Extract project_id from URL params
                return self.router.page.params.get("project_id")
        except:
            pass
        return None

    @rx.var
    def is_project_page(self) -> bool:
        """Check if we're currently in a project-specific page."""
        return self.current_project_id is not None


def sidebar_item(text: str, icon: str, href: str, is_expanded: rx.Var) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(tag=icon, size=rx.cond(is_expanded, 24, 20)),
            rx.text(
                text,
                size="4",
                display=rx.cond(is_expanded, "block", "none"),
            ),
            width="100%",
            padding_x="0.5rem",
            padding_y="0.75rem",
            align="center",
        ),
        href=href,
        underline="none",
        weight="medium",
        width="100%",
    )


def project_sidebar_item(
    text: str, icon: str, page_type: str, is_expanded: rx.Var
) -> rx.Component:
    """Create a sidebar item that links to a project-specific page."""
    return sidebar_item(
        text,
        icon,
        f"/project/{page_type}/{SidebarState.current_project_id}",
        is_expanded,
    )


def sidebar_items(is_expanded: rx.Var) -> rx.Component:
    return rx.vstack(
        sidebar_item("Home", "home", "/home", is_expanded),
        # Conditionally show project-specific items only when in a project
        rx.cond(
            SidebarState.is_project_page,
            rx.vstack(
                # Dynamic project links with current project ID
                project_sidebar_item(
                    "Dashboard", "layout-dashboard", "dashboard", is_expanded
                ),
                project_sidebar_item("Board", "kanban", "kanban", is_expanded),
                project_sidebar_item(
                    "Timeline", "chart-gantt", "timeline", is_expanded
                ),
                project_sidebar_item("Members", "users", "members", is_expanded),
                spacing="1",
                width="100%",
            ),
            rx.fragment(),  # Don't render anything if not on a project page
        ),
        spacing="1",
        width="100%",
    )


def sidebar() -> rx.Component:
    return rx.cond(
        SidebarState.is_project_page,
        rx.box(
            rx.desktop_only(
                rx.vstack(
                    rx.hstack(
                        rx.button(
                            rx.icon(
                                tag=rx.cond(
                                    DrawerState.is_desktop_expanded,
                                    "chevron-left",
                                    "chevron-right",
                                ),
                                size=20,
                            ),
                            on_click=DrawerState.toggle_desktop,
                        ),
                        width="100%",
                        justify="end",
                        padding_y="0.5em",
                    ),
                    sidebar_items(DrawerState.is_desktop_expanded),  # type: ignore
                    spacing="5",
                    padding_x="1em",
                    padding_y="1.5em",
                    align="start",
                    height="100vh",
                    min_height="100%",
                    width=rx.cond(DrawerState.is_desktop_expanded, "13em", "5em"),
                    transition="all 0.3s ease-in-out",
                    class_name="shadow-lg",
                    border_right=rx.color_mode_cond(
                        dark="2px solid rgb(38, 39, 43)", light="2px solid #E2E8F0"
                    ),
                ),
            ),
            # Not handle properly yet
            rx.mobile_and_tablet(
                rx.drawer.root(
                    rx.drawer.trigger(rx.icon(tag="menu", size=30)),
                    rx.drawer.overlay(z_index="5"),
                    rx.drawer.portal(
                        rx.drawer.content(
                            rx.vstack(
                                rx.box(
                                    rx.drawer.close(rx.icon(tag="x", size=30)),
                                    width="100%",
                                ),
                                sidebar_items(True),  # type: ignore
                                spacing="5",
                                width="100%",
                            ),
                            top="auto",
                            right="auto",
                            height="100%",
                            width="20em",
                            padding="1.5em",
                        ),
                        width="100%",
                    ),
                    direction="left",
                ),
            ),
        ),
        rx.fragment(),
    )
