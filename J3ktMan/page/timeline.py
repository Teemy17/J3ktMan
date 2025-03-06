import reflex as rx
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from J3ktMan.component import timeline, base
from typing_extensions import TypedDict


def epoch_to_date(epoch: int) -> str:
    return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d")


# Fetch the project tasks data
def get_sprint_data() -> pd.DataFrame:
    # TODO: Fetch the data from the backend
    """
    data format should be like this:
        data = {
            "id": ["SW-5", "SW-6"],
            "name": [
                "Planning",
                "Design",
            ],
            "start_date": [
                "2025-02-01",
                "2025-02-15",
            ],
            "end_date": [
                "2025-02-15",
                "2025-03-01",
            ],
        }
    """
    mock_data = {
        "id": ["SW-5", "SW-6", "SW-13", "SW-14", "SW-15", "SW-25"],
        "name": [
            "Planning",
            "Design",
            "Development",
            "Testing",
            "Deployment",
            "Post-deployment",
        ],
        "start_date": [
            "2025-01-01",
            "2025-02-15",
            "2025-01-15",
            "2025-02-20",
            "2025-03-01",
            "2025-03-10",
        ],
        "end_date": [
            "2025-02-15",
            "2025-03-01",
            "2025-02-15",
            "2025-03-05",
            "2025-03-10",
            "2025-03-25",
        ],
        "status": [
            "DONE",
            "IN PROGRESS",
            "IN PROGRESS",
            "IN PROGRESS",
            "IN PROGRESS",
            "IN PROGRESS",
        ],
    }
    return pd.DataFrame(mock_data)


class TaskDict(TypedDict):
    id: str
    name: str
    start_date: str
    end_date: str
    start_position: float
    end_position: float
    status: str


class TimelineState(rx.State):
    sprint_data: pd.DataFrame = get_sprint_data()
    current_date: str = datetime.now().strftime("%Y-%m-%d")
    months: List[str] = []
    positions: List[TaskDict] = []  # Type annotation for positions
    current_date_position: float = 0.0

    def on_mount(self):
        """Initialize all data when the component loads."""
        self.compute_months()
        self.compute_positions()
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

    def compute_positions(self):
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
        positions = []
        for _, row in self.sprint_data.iterrows():
            start_date = datetime.strptime(row["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(row["end_date"], "%Y-%m-%d")
            start_position = (
                (start_date - first_task_date).days / total_days
            ) * 100
            end_position = (
                (end_date - first_task_date).days / total_days
            ) * 100
            start_position = max(0, min(100, start_position))
            end_position = max(0, min(100, end_position))
            positions.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "start_date": row["start_date"],
                    "end_date": row["end_date"],
                    "start_position": float(start_position),
                    "end_position": float(end_position),
                }
            )
        print("Computed positions:", positions)
        self.positions = positions

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
            (current_date - first_task_date).days / total_days * 100
        )
        self.current_date_position = current_date_position

    @rx.event
    async def on_date_change(self, new_date: str) -> None:
        self.current_date = new_date
        self.compute_current_date_position()


def render_month_headers():
    """Render the month headers dynamically."""
    return rx.fragment(
        rx.foreach(
            TimelineState.months, lambda month: timeline.month_header(month)
        )
    )


def render_task_name():
    """Render the task names."""
    return rx.fragment(
        # add padding to align the task names with the timeline bars
        rx.box(padding_y="18.5px"),
        rx.foreach(
            TimelineState.positions, lambda task: timeline.task_name(task)
        ),
    )


def render_tasks():
    """Render the task rows with timeline bars."""
    return rx.fragment(
        rx.foreach(
            TimelineState.positions, lambda task: timeline.task_row(task)
        )
    )


@rx.page(route="/timeline")
def timeline_view() -> rx.Component:
    return base.base_page(
        rx.fragment(
            rx.text("Project Timeline", class_name="text-3xl font-bold mb-20"),
            rx.flex(
                # left side of the timeline (contains the tasks names)
                rx.box(
                    render_task_name(),
                    width="200px",
                    align_items="flex-start",
                ),
                # right side of the timeline (contains the timeline bars and month headers)
                rx.scroll_area(
                    rx.hstack(
                        render_month_headers(),
                    ),
                    render_tasks(),
                    width="calc(100% - 200px)",
                    align_items="flex-start",
                    position="relative",
                ),
                direction="row",
                width="100%",
                align_items="flex-start",
                spacing="0",
            ),
            width="100%",
            align_items="stretch",
            spacing="5",
            max_width="1200px",
            margin="auto",
            padding="20",
            border="1px solid #ddd",
            border_radius="5",
            type="always",
            scrollbars="horizontal",
            on_mount=TimelineState.on_mount,  # type:ignore
        )
    )
