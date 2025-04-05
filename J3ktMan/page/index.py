import reflex as rx

# Define colors and styles
COLORS = {
    "primary": "#3b82f6",
    "secondary": "#10b981",
    "accent": "#6366f1",
    "text": "#1f2937",
    "light_text": "#6b7280",
}

# Styles
navbar_style = {
    "width": "100%",
    "padding": "1rem 2rem",
    "display": "flex",
    "align_items": "center",
    "justify_content": "space-between",
    "box_shadow": "0 2px 4px rgba(0, 0, 0, 0.05)",
    "position": "fixed",
    "top": 0,
    "z_index": 1000,
}

button_primary_style = {
    "background_color": COLORS["primary"],
    "padding": "0.75rem 1.5rem",
    "border_radius": "0.375rem",
    "font_weight": "600",
    "_hover": {"background_color": "rgba(59, 130, 246, 0.9)"},
}

button_secondary_style = {
    "color": COLORS["primary"],
    "padding": "0.75rem 1.5rem",
    "border_radius": "0.375rem",
    "font_weight": "600",
    "border": f"1px solid {COLORS['primary']}",
    "_hover": {"background_color": "rgba(59, 130, 246, 0.1)"},
}

section_style = {
    "padding": "5rem 2rem",
    "display": "flex",
    "flex_direction": "column",
    "align_items": "center",
    "width": "100%",
}

card_style = {
    "border_radius": "0.5rem",
    "padding": "2rem",
    "box_shadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
    "margin": "1rem",
    "width": "100%",
    "max_width": "350px",
    "transition": "transform 0.2s",
    "_hover": {"transform": "translateY(-5px)"},
}


# Components
def navbar():
    return rx.box(
        rx.hstack(
            rx.heading("J3ktMan", size="5", color=COLORS["primary"]),
            rx.spacer(),
            rx.hstack(
                rx.color_mode_cond(
                    light=rx.icon_button(
                        rx.icon("moon"),
                        variant="ghost",
                        aria_label="Dark mode",
                        on_click=rx.toggle_color_mode,
                        size="3",
                    ),
                    dark=rx.icon_button(
                        rx.icon("sun"),
                        variant="ghost",
                        aria_label="Light mode",
                        on_click=rx.toggle_color_mode,
                        size="3",
                    ),
                ),
                rx.button(
                    "Sign in",
                    style=button_primary_style,  # type: ignore
                    on_click=rx.redirect("/signin"),
                ),
                spacing="7",
            ),
            width="100%",
        ),
        style=navbar_style,  # type: ignore
        border_bottom=rx.color_mode_cond(
            dark="2px solid rgb(38, 39, 43)", light="2px solid #E2E8F0"
        ),
        background_color=rx.color_mode_cond(dark="#1a202c", light="white"),
    )


def hero_section():
    return rx.box(
        rx.vstack(
            rx.heading(
                "Manage Projects with Ease and Efficiency",
                size="7",
                text_align="center",
                margin_bottom="1.5rem",
            ),
            rx.text(
                "J3ktman helps teams organize, track, and deliver their best work with a simple yet powerful project management tool.",
                font_size="1.25rem",
                color=COLORS["light_text"],
                text_align="center",
                max_width="800px",
                margin_bottom="2.5rem",
            ),
            rx.hstack(
                rx.button(
                    "Get Started",
                    style=button_primary_style,  # type: ignore
                    on_click=rx.redirect("/signup"),
                ),
            ),
            rx.hstack(
                rx.image(
                    src=rx.color_mode_cond(
                        dark="/pics/j3ktman_kanban.png",
                        light="/pics/j3ktman_kanban_light.png",
                    ),
                    width="80%",
                    max_width="1000px",
                    margin_top="3rem",
                    border_radius="0.5rem",
                    box_shadow="0 10px 25px rgba(0, 0, 0, 0.1)",
                    alt="J3ktman kanban Preview",
                ),
                rx.image(
                    src=rx.color_mode_cond(
                        dark="/pics/j3ktman_dashboard.png",
                        light="/pics/j3ktman_dashboard_light.png",
                    ),
                    width="80%",
                    max_width="1000px",
                    margin_top="3rem",
                    border_radius="0.5rem",
                    box_shadow="0 10px 25px rgba(0, 0, 0, 0.1)",
                    alt="J3ktman dashboard Preview",
                ),
                spacing="5",
                justify="center",
            ),
            spacing="2",
            align_items="center",
            padding_top="8rem",
            padding_bottom="5rem",
        ),
        style=section_style,  # type: ignore
        background_color=rx.color_mode_cond(dark="#151618", light="#f9fafb"),
    )


def feature_card(icon, title, description):
    return rx.box(
        rx.vstack(
            rx.box(
                rx.icon(
                    icon,
                    color=COLORS["primary"],
                    font_size="2rem",
                ),
                background_color="rgba(59, 130, 246, 0.1)",
                padding="1rem",
                border_radius="0.5rem",
                margin_bottom="1.5rem",
            ),
            rx.heading(title, size="3", margin_bottom="1rem"),
            rx.text(
                description,
                color=COLORS["light_text"],
                text_align="center",
            ),
            align_items="center",
            spacing="1",
        ),
        style=card_style,  # type: ignore
        box_shadow=rx.color_mode_cond(
            dark="0 4px 6px rgba(0, 0, 0, 0.4)",
            light="0 4px 6px rgba(0, 0, 0, 0.1)",
        ),
    )


def features_section():
    return rx.box(
        rx.vstack(
            rx.heading(
                "Features Designed for Modern Teams",
                size="6",
                margin_bottom="1rem",
            ),
            rx.text(
                "Everything you need to manage projects effectively in one place",
                color=COLORS["light_text"],
                margin_bottom="3rem",
                font_size="1.1rem",
            ),
            rx.hstack(
                feature_card(
                    "calendar",
                    "Task Management",
                    "Create, assign, and track tasks, priorities, and custom fields.",
                ),
                feature_card(
                    "bar-chart",
                    "Progress Tracking",
                    "Visualize project progress with interactive charts and real-time status updates.",
                ),
                feature_card(
                    "users",
                    "Team Collaboration",
                    "collaborate with your team members. Invite new members and assign tasks.",
                ),
                spacing="2",
                flex_wrap="wrap",
                justify="center",
            ),
            align_items="center",
            width="100%",
        ),
        style=section_style,  # type: ignore
        box_shadow=rx.color_mode_cond(
            dark="0 4px 6px rgba(0, 0, 0, 0.4)",
            light="0 4px 6px rgba(0, 0, 0, 0.1)",
        ),
    )


def how_it_works():
    return rx.box(
        rx.vstack(
            rx.heading(
                "How J3ktMan Works",
                size="6",
                margin_bottom="1rem",
            ),
            rx.text(
                "Get started in minutes with our intuitive workflow",
                color=COLORS["light_text"],
                margin_bottom="3rem",
                font_size="1.1rem",
            ),
            rx.hstack(
                rx.vstack(
                    rx.heading("1", size="5", color=COLORS["primary"]),
                    rx.heading("Create a Project", size="3", margin_top="1rem"),
                    rx.text(
                        "Set up your project with goals, timeline, and team members.",
                        color=COLORS["light_text"],
                        text_align="center",
                    ),
                    align_items="center",
                    padding="2rem",
                    border_radius="0.5rem",
                    width="250px",
                    box_shadow=rx.color_mode_cond(
                        dark="0 4px 6px rgba(0, 0, 0, 0.4)",
                        light="0 4px 6px rgba(0, 0, 0, 0.1)",
                    ),
                ),
                rx.vstack(
                    rx.heading("2", size="5", color=COLORS["primary"]),
                    rx.heading("Add Tasks", size="3", margin_top="1rem"),
                    rx.text(
                        "Break down your project into manageable tasks and assign them.",
                        color=COLORS["light_text"],
                        text_align="center",
                    ),
                    align_items="center",
                    padding="2rem",
                    border_radius="0.5rem",
                    width="250px",
                    box_shadow=rx.color_mode_cond(
                        dark="0 4px 6px rgba(0, 0, 0, 0.4)",
                        light="0 4px 6px rgba(0, 0, 0, 0.1)",
                    ),
                ),
                rx.vstack(
                    rx.heading("3", size="5", color=COLORS["primary"]),
                    rx.heading("Track Progress", size="3", margin_top="1rem"),
                    rx.text(
                        "Monitor progress, update statuses, and stay on schedule.",
                        color=COLORS["light_text"],
                        text_align="center",
                    ),
                    align_items="center",
                    padding="2rem",
                    border_radius="0.5rem",
                    box_shadow=rx.color_mode_cond(
                        dark="0 4px 6px rgba(0, 0, 0, 0.4)",
                        light="0 4px 6px rgba(0, 0, 0, 0.1)",
                    ),
                    width="250px",
                ),
                spacing="2",
                flex_wrap="wrap",
                justify="center",
            ),
            align_items="center",
            width="100%",
        ),
        style=section_style,  # type: ignore
    )


def footer():
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("J3ktman", size="3", color=COLORS["primary"]),
                    rx.text(
                        "Modern project management for productive teams",
                        color=COLORS["light_text"],
                        margin_top="0.5rem",
                    ),
                    align_items="flex-start",
                ),
                rx.spacer(),
                width="100%",
                flex_wrap="wrap",
            ),
            rx.divider(margin_y="2rem"),
            rx.text(
                "© 2025 J3ktman. All rights reserved.",
                color=COLORS["light_text"],
                font_size="0.9rem",
            ),
            width="100%",
            max_width="1200px",
        ),
        padding="4rem 2rem",
        width="100%",
        display="flex",
        justify_content="center",
    )


def index():
    return rx.box(
        navbar(),
        hero_section(),
        features_section(),
        how_it_works(),
        footer(),
        width="100%",
    )
