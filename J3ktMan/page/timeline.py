import reflex as rx
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from J3ktMan.component import timeline, base
from functools import partial


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
            "2025-02-01",
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
    }
    return pd.DataFrame(mock_data)


class TimelineState(rx.State):
    sprint_data: pd.DataFrame = get_sprint_data()
    current_date: str = datetime.now().strftime(
        "%Y-%m-%d"
    )  # The vertical line date

    months: List[str] = []
    positions: List[Dict[str, Any]] = []
    current_date_position: float = 0.0

    def on_mount(self):
        """Initialize all data when the component loads."""
        self.compute_months()
        self.compute_positions()
        self.compute_current_date_position()

        print(self.months)

    def compute_months(self) -> None:
        """
        Compute the timeline's months based on the start and end dates
        of the tasks by rounding the dates to the nearest whole month.
        """
        all_dates = (
            self.sprint_data["start_date"].tolist()
            + self.sprint_data["end_date"].tolist()
        )

        start = min(datetime.strptime(d, "%Y-%m-%d") for d in all_dates)
        end = max(datetime.strptime(d, "%Y-%m-%d") for d in all_dates)

        # Round to whole months
        start = datetime(start.year, start.month, 1)
        # If the end date is in December, move to the next year
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
        """
        Compute the positions of the tasks on the timeline based on the
        start and end dates of the tasks.
        """
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

        # Add some padding to the first and last dates
        first_task_date = datetime(
            first_task_date.year, first_task_date.month, 1
        )
        if last_task_date.month == 12:
            last_task_date = datetime(last_task_date.year + 1, 1, 31)
        else:
            last_task_date = datetime(
                last_task_date.year, last_task_date.month + 2, 1
            ) - timedelta(days=1)

        # Calculate the total number of days between the first and last task
        total_days = (last_task_date - first_task_date).days

        positions = []
        for _, row in self.sprint_data.iterrows():
            start_date = datetime.strptime(row["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(row["end_date"], "%Y-%m-%d")

            # Calculate the position of the task on the timeline as percentages
            start_position = (
                (start_date - first_task_date).days / total_days
            ) * 100
            end_position = (
                (end_date - first_task_date).days / total_days
            ) * 100

            positions.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "start_date": row["start_date"],
                    "end_date": row["end_date"],
                    "start_position": start_position,
                    "end_position": end_position,
                }
            )

        self.positions = positions

    def compute_current_date_position(self):
        """
        Compute the position of the current date line on the timeline
        and store it in state.
        """
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

        # Calculate the position of the current date line
        current_date = datetime.strptime(self.current_date, "%Y-%m-%d")
        current_date_position = (
            (current_date - first_task_date).days / total_days * 100
        )

        self.current_date_position = current_date_position

    @rx.event
    async def on_date_change(self, new_date: str) -> None:
        """
        Handle the change of the current date and update the position
        of the current date line on the timeline.
        """
        self.current_date = new_date
        self.compute_current_date_position()


def render_month_headers():
    """Render the month headers dynamically."""
    return rx.fragment(
        rx.foreach(
            TimelineState.months, lambda month: timeline.month_header(month)
        )
    )


def render_task_rows():
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
            rx.hstack(
                rx.box(
                    rx.text(""),
                    width="25%",
                ),
                rx.hstack(
                    render_month_headers(),
                    class_name="w-full relative",
                ),
                width="100%",
            ),
            rx.box(
                rx.box(
                    position="absolute",
                    left=f"{TimelineState.current_date_position}%",
                    top="0",
                    bottom="0",
                    width="1px",
                    background_color="#666",
                    z_index="1",
                ),
                render_task_rows(),
                position="relative",
                width="100%",
            ),
            width="100%",
            align_items="stretch",
            spacing="5",
            max_wdith="1200px",
            margin="auto",
            padding="20",
            border="1px solid #ddd",
            border_radius="5",
            on_mount=partial(TimelineState.on_mount, TimelineState),
        )
    )
