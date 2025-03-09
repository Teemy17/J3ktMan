import reflex as rx
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from J3ktMan.component import timeline, base
from typing_extensions import TypedDict


def epoch_to_date(epoch: int) -> str:
    return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d")


def get_milestone_data() -> pd.DataFrame:
    # TODO: Fetch the data from the backend
    """
    data format should be like this:
        data = [
            {
                "id": 1,
                "project_id": 1,
                "name": "Milestone 1",
                "description": "First milestone",
                "due_date": 1640995200,  # Epoch timestamp
            },
        ]
    """
    mock_data = [
        {
            "id": 1,
            "project_id": 1,
            "name": "Milestone 1",
            "description": "First milestone",
            "due_date": 1735689600,  # 2025-01-01 00:00:00 UTC
        },
        {
            "id": 2,
            "project_id": 1,
            "name": "Milestone 2",
            "description": "Second milestone",
            "due_date": 1739462400,  # 2025-02-15 00:00:00 UTC
        },
        {
            "id": 3,
            "project_id": 1,
            "name": "Milestone 3",
            "description": "Third milestone",
            "due_date": 1741075200,  # 2025-03-01 00:00:00 UTC
        },
        {
            "id": 4,
            "project_id": 1,
            "name": "Milestone 4",
            "description": "Fourth milestone",
            "due_date": 1748016000,  # 2025-06-23 00:00:00 UTC
        },
    ]

    # Convert epoch timestamps to date strings
    data = [
        {
            "id": milestone["id"],
            "project_id": milestone["project_id"],
            "name": milestone["name"],
            "description": milestone["description"],
            "due_date": epoch_to_date(milestone["due_date"]),
        }
        for milestone in mock_data
    ]
    return pd.DataFrame(data)


# Fetch the project tasks data
def get_sprint_data() -> pd.DataFrame:
    # TODO: Fetch the data from the backend
    """
    data format should be like this:
        data = [
            {
                "id": "SW-5",
                "name": "Planning",
                "description": "Planning the project",
                "milestone_id": 1,
                "status_id": 1,
                "priority": "HIGH",
                "start_date": 1640995200,  # Epoch timestamp
                "end_date": 1644844800,    # Epoch timestamp
            },
        ]
    """
    mock_data = [
        {
            "id": "SW-5",
            "name": "Planning",
            "description": "Planning the project",
            "milestone_id": 1,
            "status_id": 1,  # 1 maps to "DONE"
            "priority": "HIGH",
            "start_date": 1735689600,  # 2025-01-01 00:00:00 UTC
            "end_date": 1736918400,  # 2025-01-15 00:00:00 UTC
        },
        {
            "id": "SW-6",
            "name": "Design",
            "description": "Designing the system",
            "milestone_id": 1,
            "status_id": 2,  # 2 maps to "IN PROGRESS"
            "priority": "MEDIUM",
            "start_date": 1739462400,  # 2025-02-15 00:00:00 UTC
            "end_date": 1739856000,  # 2025-02-20 00:00:00 UTC
        },
        {
            "id": "SW-13",
            "name": "Development",
            "description": "Developing features",
            "milestone_id": 2,
            "status_id": 2,  # 2 maps to "IN PROGRESS"
            "priority": "HIGH",
            "start_date": 1736304000,  # 2025-01-10 00:00:00 UTC
            "end_date": 1736918400,  # 2025-01-15 00:00:00 UTC
        },
        {
            "id": "SW-14",
            "name": "Testing",
            "description": "Testing the system",
            "milestone_id": 3,
            "status_id": 2,  # 2 maps to "IN PROGRESS"
            "priority": "MEDIUM",
            "start_date": 1739856000,  # 2025-02-20 00:00:00 UTC
            "end_date": 1741075200,  # 2025-03-01 00:00:00 UTC
        },
        {
            "id": "SW-15",
            "name": "Deployment",
            "description": "Deploying the system",
            "milestone_id": 3,
            "status_id": 2,  # 2 maps to "IN PROGRESS"
            "priority": "HIGH",
            "start_date": 1741075200,  # 2025-03-01 00:00:00 UTC
            "end_date": 1741372800,  # 2025-03-05 00:00:00 UTC
        },
        {
            "id": "SW-25",
            "name": "Post-deployment",
            "description": "Post-deployment review",
            "milestone_id": 4,
            "status_id": 2,  # 2 maps to "IN PROGRESS"
            "priority": "LOW",
            "start_date": 1741680000,  # 2025-03-10 00:00:00 UTC
            "end_date": 1742188800,  # 2025-03-15 00:00:00 UTC
        },
        {
            "id": "SW-30",
            "name": "Review",
            "description": "Final review",
            "milestone_id": 4,
            "status_id": 2,  # 2 maps to "IN PROGRESS"
            "priority": "LOW",
            "start_date": 1748016000,  # 2025-06-23 00:00:00 UTC
            "end_date": 1748508000,  # 2025-06-28 00:00:00 UTC
        },
    ]

    # Convert epoch timestamps to date strings and map status_id to status
    status_map = {1: "DONE", 2: "IN PROGRESS"}
    data = [
        {
            "id": task["id"],
            "name": task["name"],
            "start_date": epoch_to_date(task["start_date"]),
            "end_date": epoch_to_date(task["end_date"]),
            "status": status_map.get(task["status_id"], "IN PROGRESS"),
            "milestone_id": task["milestone_id"],
        }
        for task in mock_data
    ]
    return pd.DataFrame(data)


class TaskDict(TypedDict):
    id: str
    name: str
    start_date: str
    end_date: str
    start_position: float
    end_position: float
    status: str
    milestone_id: int


class MilestoneDict(TypedDict):
    id: int
    project_id: int
    name: str
    description: str
    due_date: str
    tasks: List[TaskDict]
    start_position: float
    end_position: float


class TimelineState(rx.State):
    sprint_data: pd.DataFrame = get_sprint_data()
    milestone_data: pd.DataFrame = get_milestone_data()
    current_date: str = datetime.now().strftime("%Y-%m-%d")
    months: List[str] = []
    milestones: List[MilestoneDict] = []
    expanded_milestones: Dict[int, bool] = (
        {}
    )  # Track which milestones are expanded
    current_date_position: float = 0.0

    def on_mount(self):
        """Initialize all data when the component loads."""
        self.compute_months()
        self.compute_milestones()
        self.compute_current_date_position()

    def compute_months(self) -> None:
        all_dates = (
            self.sprint_data["start_date"].tolist()
            + self.sprint_data["end_date"].tolist()
        )
        start = min(datetime.strptime(d, "%Y-%m-%d") for d in all_dates)
        end = max(datetime.strptime(d, "%Y-%m-%d") for d in all_dates)
        start = datetime(start.year, start.month, 1)
        if end.month == 12:
            end = datetime(end.year + 1, 1, 1)
        else:
            end = datetime(end.year, end.month + 1, 1)
        months = []
        current = start
        while current < end:
            months.append(current.strftime("%b").upper())
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)
        self.months = months

    def compute_milestones(self):
        # Compute the overall timeline range
        all_dates = (
            self.sprint_data["start_date"].tolist()
            + self.sprint_data["end_date"].tolist()
        )
        first_task_date = min(
            datetime.strptime(d, "%Y-%m-%d") for d in all_dates
        )
        last_task_date = max(
            datetime.strptime(d, "%Y-%m-%d") for d in all_dates
        )
        total_days = (last_task_date - first_task_date).days

        # Group tasks by milestone
        milestones = []
        for _, milestone in self.milestone_data.iterrows():
            # Get all tasks for this milestone
            tasks = self.sprint_data[
                self.sprint_data["milestone_id"] == milestone["id"]
            ]
            task_positions = []
            if not tasks.empty:
                # Compute positions for each task
                for _, task in tasks.iterrows():
                    start_date = datetime.strptime(
                        task["start_date"], "%Y-%m-%d"
                    )
                    end_date = datetime.strptime(task["end_date"], "%Y-%m-%d")
                    start_position = (
                        (start_date - first_task_date).days / total_days
                    ) * 100
                    end_position = (
                        (end_date - first_task_date).days / total_days
                    ) * 100
                    start_position = max(0, min(100, start_position))
                    end_position = max(0, min(100, end_position))
                    task_positions.append(
                        {
                            "id": task["id"],
                            "name": task["name"],
                            "start_date": task["start_date"],
                            "end_date": task["end_date"],
                            "start_position": float(start_position),
                            "end_position": float(end_position),
                            "status": task["status"],
                            "milestone_id": task["milestone_id"],
                        }
                    )

                # Compute milestone's overall start and end positions
                milestone_start = min(
                    task["start_position"] for task in task_positions
                )
                milestone_end = max(
                    task["end_position"] for task in task_positions
                )

                milestones.append(
                    {
                        "id": milestone["id"],
                        "project_id": milestone["project_id"],
                        "name": milestone["name"],
                        "description": milestone["description"],
                        "due_date": milestone["due_date"],
                        "start_position": milestone_start,
                        "end_position": milestone_end,
                        "tasks": task_positions,
                    }
                )

        self.milestones = milestones
        # Initialize expanded state for each milestone
        self.expanded_milestones = {
            milestone["id"]: True for milestone in milestones
        }

    def compute_current_date_position(self):
        all_dates = (
            self.sprint_data["start_date"].tolist()
            + self.sprint_data["end_date"].tolist()
        )
        first_task_date = min(
            datetime.strptime(d, "%Y-%m-%d") for d in all_dates
        )
        last_task_date = max(
            datetime.strptime(d, "%Y-%m-%d") for d in all_dates
        )
        total_days = (last_task_date - first_task_date).days
        current_date = datetime.strptime(self.current_date, "%Y-%m-%d")
        current_date_position = (
            (current_date - first_task_date).days / total_days
        ) * 100
        self.current_date_position = current_date_position

    def toggle_milestone(self, milestone_id: int):
        """Toggle the expanded state of a milestone."""
        self.expanded_milestones[milestone_id] = (
            not self.expanded_milestones.get(milestone_id, False)
        )


def render_month_headers():
    """Render the month headers dynamically."""
    return rx.fragment(
        rx.foreach(
            TimelineState.months, lambda month: timeline.month_header(month)
        )
    )


def render_task_name():
    """Render the milestone names and their tasks (when expanded)."""

    def render_milestone_name(milestone):
        is_expanded = TimelineState.expanded_milestones[milestone["id"]]
        return rx.vstack(
            rx.hstack(
                rx.icon(
                    # tag="chevron-right" if not is_expanded else "chevron-down",
                    tag=rx.cond(
                        is_expanded,
                        "chevron-down",
                        "chevron-right",
                    ),
                    on_click=lambda: TimelineState.toggle_milestone(
                        milestone["id"]  # type:ignore
                    ),
                    cursor="pointer",
                    margin_right="0.5rem",
                ),
                rx.text(
                    milestone["name"],
                    color="#eee",
                    font_size="14px",
                    font_weight="bold",
                ),
                spacing="2",
                align_items="center",
                width="100%",
                height="40px",
                min_height="40px",
            ),
            rx.cond(
                is_expanded,
                rx.foreach(
                    milestone["tasks"],
                    lambda task: rx.box(
                        rx.hstack(
                            rx.box(
                                width="12px",
                                height="12px",
                                background_color=timeline.get_status_color(
                                    str(task["status"])
                                ),
                                border_radius="2px",
                            ),
                            rx.text(
                                task["name"],
                                color="#eee",
                                font_size="14px",
                                font_weight="medium",
                            ),
                            spacing="2",
                            align_items="center",
                            # width="100%",
                            # height="40px",
                        ),
                        padding_left="1.5rem",
                        height="40px",
                    ),
                ),
            ),
            width="100%",
            spacing="0",
            align_items="stretch",
            border_bottom="1px solid #4d4d4d",
        )

    return rx.fragment(
        rx.box(
            padding_y="18.5px"
        ),  # ensure the first task name aligns with the first timeline bar
        rx.foreach(
            TimelineState.milestones,
            render_milestone_name,
        ),
    )


def render_tasks():
    """Render the milestone rows with timeline bars (collapsed or expanded)."""

    def render_milestone_row(milestone: MilestoneDict) -> rx.Component:
        is_expanded = TimelineState.expanded_milestones[milestone["id"]]
        return rx.vstack(
            # Milestone bar
            rx.hstack(
                rx.box(
                    rx.box(
                        position="absolute",
                        left=f"{milestone['start_position']}%",
                        width=f"{milestone['end_position'] - milestone['start_position']}%",
                        height="20px",
                        background_color="#5b279c",
                        border_radius="3px",
                        border="1px solid white",  # Make it visible
                        padding_y="0.5rem",
                    ),
                    position="relative",
                    height="100%",
                    width="100%",
                ),
                width="100%",
                padding_y="0.5rem",
                border_bottom=rx.cond(
                    is_expanded, "none", "1px solid #4d4d4d"
                ),
                height="41px",
            ),
            # Task bars
            rx.cond(
                is_expanded,
                rx.foreach(
                    milestone["tasks"],
                    lambda task: timeline.task_row(task),
                ),
            ),
            spacing="0",
            width="100%",  # Force the container to take full width
        )

    return rx.fragment(
        rx.foreach(
            TimelineState.milestones,
            render_milestone_row,
        )
    )


@rx.page(route="/timeline")
def timeline_view() -> rx.Component:
    return base.base_page(
        rx.fragment(
            rx.text("Project Timeline", class_name="text-3xl font-bold mb-20"),
            rx.flex(
                rx.box(
                    render_task_name(),
                    width="200px",
                    align_items="flex-start",
                    height="auto",
                ),
                rx.scroll_area(
                    rx.vstack(
                        rx.hstack(
                            render_month_headers(),
                            spacing="0",
                            width="100%",
                            overflow_x="auto",
                        ),
                        render_tasks(),
                        width="100%",
                        spacing="0",
                        align_items="stretch",
                        # position="relative",
                    ),
                    width="calc(100% - 200px)",
                    height="auto",
                    overflow_x="auto",
                    scrollbars="horizontal",
                    # position="relative",
                ),
                direction="row",
                width="100%",
                align_items="stetch",
                spacing="0",
                height="auto",
            ),
            width="100%",
            align_items="stretch",
            spacing="5",
            max_width="1200px",
            margin="auto",
            padding="20",
            border="1px solid #ddd",
            border_radius="5",
            on_mount=TimelineState.on_mount,  # type:ignore
        )
    )
