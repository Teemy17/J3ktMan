import reflex as rx
from J3ktMan.component.project_card import project_card
from J3ktMan.component.base import base_page

# Sample project data
projects = [
    {
        "name": "Project 1",
        "description": "Lorem ipsum lodpr lamo jwjwj kekw\nsadad moel aal p apkda",
        "comments": 12,
        "files": 0,
    },
    {
        "name": "Project 2",
        "description": "Another project description example.",
        "comments": 8,
        "files": 2,
    },
    {
        "name": "Project 3",
        "description": "Lorem ipus.",
        "comments": 5,
        "files": 1,
    },
    {
        "name": "Project 4",
        "description": "Another project description example.",
        "comments": 8,
        "files": 2,
    }
]

def home() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.text("Home", size="7", weight="bold"),
            rx.grid(
                rx.foreach(
                    projects,
                    lambda project: project_card(
                        name=project["name"],
                        description=project["description"],
                        comments=project["comments"],
                        files=project["files"],
                    )
                ),
                columns="3",
                spacing="6",
                align="start",
                width="100%"
            )
        )
    )
