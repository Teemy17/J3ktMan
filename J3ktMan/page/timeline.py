from datetime import datetime, timedelta
from typing import Any, Dict, List

import pandas as pd
import reflex as rx
from typing_extensions import TypedDict

import J3ktMan.model.project
from J3ktMan.component import base
from J3ktMan.component.create_milestone_dialog import create_milestone_dialog
from J3ktMan.component.protected import protected_page_with
from J3ktMan.component.task_dialog import task_dialog
from J3ktMan.component.create_task_dialog import create_task_dialog
from J3ktMan.state.project import (
    State as ProjectState,
    Data as ProjectData,
    Milestone as MilestoneData,
)
from J3ktMan.utils import epoch_to_date
import calendar


def get_milestone_data(project_data: ProjectData) -> pd.DataFrame:
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
    data = [
        {
            "id": milestone.id,
            "name": milestone.name,
            "description": milestone.description,
            "due_date": None,
        }
        for milestone in project_data.milestones_by_id.values()
    ]
    return pd.DataFrame(data)


# Fetch the project tasks data
def get_sprint_data(project_data: ProjectData) -> pd.DataFrame:
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
            "start_date": 1748016000,  # 2025-05-23 00:00:00 UTC
            "end_date": 1748508000,  # 2025-05-28 00:00:00 UTC
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

    data = [
        {
            "id": task.id,
            "name": task.name,
            "start_date": (
                epoch_to_date(task.start_date)
                if task.start_date is not None
                else None
            ),
            "end_date": (
                epoch_to_date(task.end_date)
                if task.end_date is not None
                else None
            ),
            "status": project_data.statuses_by_id[task.status_id].name,
            "milestone_id": task.milestone_id,
        }
        for task in project_data.tasks_by_id.values()
    ]
    return pd.DataFrame(data)


class TaskDict(TypedDict):
    id: int
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


MIN_MONTH_COUNT = 48


class MonthRange(rx.Base):
    month: int
    year: int
    day_count: int
    string: str


def count_month(
    start_date: datetime,
    end_date: datetime,
) -> int:
    """Calculate the number of months between two dates."""
    month_count = 0

    start_date = datetime(
        start_date.year, start_date.month, 1
    )  # Set to the first day of the month
    end_date = datetime(
        end_date.year, end_date.month, 1
    )  # Set to the first day of the month

    while start_date < end_date:
        month_count += 1
        start_date = datetime(
            start_date.year + (start_date.month // 12),
            (start_date.month % 12) + 1,
            1,
        )

    return month_count


class DateRange(rx.Base):
    left: float
    width: float
    start_time: str | None
    end_time: str | None


class TaskRender(rx.Base):
    id: int
    date_range: DateRange | None


class MilestoneRender(rx.Base):
    id: int
    tasks: List[TaskRender]
    date_range: DateRange | None


class TimelineState(rx.State):
    sprint_data: pd.DataFrame = pd.DataFrame([])
    milestone_data: pd.DataFrame = pd.DataFrame([])
    current_date: datetime = datetime.now()
    months: List[str] = []
    month_widths: List[float] = []
    milestones: List[MilestoneDict] = []
    expanded_milestones: Dict[int, bool] = (
        {}
    )  # Track which milestones are expanded
    current_date_position: float = 0.0
    hover_text: str = ""

    current_project_id: int | None = None
    current_project: J3ktMan.model.project.Project | None = None

    @rx.event
    async def on_mount(self):
        project_state = await self.get_state(ProjectState)

        if project_state.data is None:
            return

        milestones = project_state.milestones
        self.expanded_milestones = {
            milestone.id: False for milestone in milestones
        }

        # self.sprint_data = get_sprint_data(project_state.data)
        # self.milestone_data = get_milestone_data(project_state.data)

        # """Initialize all data when the component loads."""
        # self.compute_months()
        # self.compute_milestones()
        # self.compute_current_date_position()

    def compute_months(self) -> None:
        all_dates = [
            x for x in self.sprint_data["start_date"].tolist() if x is not None
        ] + [x for x in self.sprint_data["end_date"].tolist() if x is not None]

        if len(all_dates) == 0:
            pass
        else:
            start = min(datetime.strptime(d, "%Y-%m-%d") for d in all_dates)
            end = max(datetime.strptime(d, "%Y-%m-%d") for d in all_dates)
            timeline_start = datetime(start.year, start.month, 1) - timedelta(
                days=30
            )
            timeline_end = datetime(end.year, end.month, 1) + timedelta(
                days=30
            )
            if timeline_end.month == 12:
                timeline_end = datetime(timeline_end.year + 1, 1, 1)
            else:
                timeline_end = datetime(
                    timeline_end.year, timeline_end.month + 1, 1
                )

            total_days = (timeline_end - timeline_start).days

            months = []
            month_widths = []
            current = timeline_start
            while current < timeline_end:
                months.append(current.strftime("%b").upper())
                if current.month == 12:
                    next_month = datetime(current.year + 1, 1, 1)
                else:
                    next_month = datetime(current.year, current.month + 1, 1)
                current = next_month

            total_months = len(months)
            month_width = 100 / total_months
            month_widths = [month_width] * total_months

            self.months = months
            self.month_widths = month_widths

    def compute_milestones(self):
        # Compute the overall timeline range (including padding)
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
        timeline_start = datetime(
            first_task_date.year, first_task_date.month, 1
        ) - timedelta(days=30)
        timeline_end = datetime(
            last_task_date.year, last_task_date.month, 1
        ) + timedelta(days=30)
        if timeline_end.month == 12:
            timeline_end = datetime(timeline_end.year + 1, 1, 1)
        else:
            timeline_end = datetime(
                timeline_end.year, timeline_end.month + 1, 1
            )

        total_days = (timeline_end - timeline_start).days

        # Calculate the month boundaries in days
        month_boundaries = []
        current = timeline_start
        while current <= timeline_end:
            days_from_start = (current - timeline_start).days
            month_boundaries.append(days_from_start)
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)

        # Calculate the total width of the timeline in pixels
        total_months = len(month_boundaries) - 1  # Number of months
        total_width_px = total_months * 300  # 300px per month
        month_width_px = 300  # Fixed width per month

        # Group tasks by milestone
        milestones = []
        for _, milestone in self.milestone_data.iterrows():
            tasks = self.sprint_data[
                self.sprint_data["milestone_id"] == milestone["id"]
            ]
            task_positions = []
            if not tasks.empty:
                for _, task in tasks.iterrows():
                    start_date = datetime.strptime(
                        task["start_date"], "%Y-%m-%d"
                    )
                    end_date = datetime.strptime(task["end_date"], "%Y-%m-%d")
                    start_days = (start_date - timeline_start).days
                    end_days = (end_date - timeline_start).days

                    # Find the month index for start and end dates
                    start_month_idx = 0
                    end_month_idx = 0
                    for i in range(len(month_boundaries) - 1):
                        if (
                            month_boundaries[i]
                            <= start_days
                            < month_boundaries[i + 1]
                        ):
                            start_month_idx = i
                            start_fraction = (
                                start_days - month_boundaries[i]
                            ) / (month_boundaries[i + 1] - month_boundaries[i])
                        if (
                            month_boundaries[i]
                            <= end_days
                            < month_boundaries[i + 1]
                        ):
                            end_month_idx = i
                            end_fraction = (end_days - month_boundaries[i]) / (
                                month_boundaries[i + 1] - month_boundaries[i]
                            )

                    # Calculate the pixel position within the month
                    start_position_px = (start_month_idx * month_width_px) + (
                        start_fraction * month_width_px  # type: ignore
                    )
                    end_position_px = (end_month_idx * month_width_px) + (
                        end_fraction * month_width_px  # type: ignore
                    )

                    # Convert to percentages
                    start_position = (start_position_px / total_width_px) * 100
                    end_position = (end_position_px / total_width_px) * 100
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
        self.expanded_milestones = {
            milestone["id"]: False for milestone in milestones
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

    def show_task_creation_dialog(self):
        """Show the task creation dialog."""

    @rx.var
    def total_width(self) -> int:
        """Compute the total width of the timeline in pixels based on the number of months."""
        return len(self.months) * 300

    @rx.var(cache=True)
    async def task_date_rnage(self) -> tuple[datetime, datetime] | None:
        project_state = await self.get_state(ProjectState)

        if project_state.data is None:
            return None

        # Get the start and end dates of the tasks
        all_dates = [
            datetime.fromtimestamp(x.start_date)
            for x in project_state.data.tasks_by_id.values()
            if x.start_date is not None
        ] + [
            datetime.fromtimestamp(x.end_date)
            for x in project_state.data.tasks_by_id.values()
            if x.end_date is not None
        ]

        if len(all_dates) == 0:
            return None

        start = min(all_dates)
        end = max(all_dates)

        return (start, end)

    @rx.var(cache=True)
    async def all_month_ranges(self) -> list[MonthRange]:
        task_date = await self.task_date_rnage

        if task_date is not None:
            start_date, end_date = task_date
            month_count = count_month(start_date, end_date)
            if month_count < MIN_MONTH_COUNT:
                month_count = MIN_MONTH_COUNT

            months = []
            current = start_date
            for _ in range(month_count):
                months.append(
                    MonthRange(
                        month=current.month,
                        year=current.year,
                        day_count=calendar.monthrange(
                            current.year, current.month
                        )[1],
                        string=current.strftime("%b %Y"),
                    )
                )
                current += timedelta(days=30)

            return months
        else:
            current_date = datetime(
                self.current_date.year, self.current_date.month, 1
            )

            # starting from the current date - 24 months and forwards to the
            # current date + 24 months
            starting = datetime(current_date.year - 2, current_date.month, 1)
            ending = datetime(current_date.year + 2, current_date.month, 1)

            months = []
            current = starting
            while current < ending:
                day_count = calendar.monthrange(current.year, current.month)[1]
                months.append(
                    MonthRange(
                        month=current.month,
                        year=current.year,
                        day_count=day_count,
                        string=current.strftime("%b %Y"),
                    )
                )
                current += timedelta(days=day_count)

            return months

    @rx.var(cache=True)
    async def total_days(self) -> int:
        """Compute the total number of days in the timeline."""
        all_month_ranges = await self.all_month_ranges
        total_days = sum(month.day_count for month in all_month_ranges)
        return total_days

    @rx.var(cache=True)
    async def total_width_pixels(self) -> int:
        """Compute the total width of the timeline in pixels."""
        return await self.total_days * 10

    @rx.var(cache=True)
    async def render_milestone(self) -> list[MilestoneRender]:
        all_month_ranges = await self.all_month_ranges
        total_days = await self.total_days
        first_month = datetime(
            all_month_ranges[0].year, all_month_ranges[0].month, 1
        )

        project_state = await self.get_state(ProjectState)

        if project_state.data is None:
            return []

        data = project_state.data

        milestone_renders = []
        for milestone in project_state.milestones:
            task_renders = []
            for task in milestone.task_ids:
                task_data = data.tasks_by_id[task]
                start_info = None
                end_info = None

                if task_data.start_date is not None:
                    start_date = datetime.fromtimestamp(task_data.start_date)
                    delta = start_date - first_month
                    left_percent = (delta.days / total_days) * 100

                    start_info = (
                        left_percent,
                        datetime.strftime(start_date, "%Y-%m-%d"),
                    )

                if task_data.end_date is not None:
                    end_date = datetime.fromtimestamp(task_data.end_date)
                    delta = end_date - first_month
                    left_percent = (delta.days / total_days) * 100

                    end_info = (
                        left_percent,
                        datetime.strftime(end_date, "%Y-%m-%d"),
                    )

                date_range = None
                match (start_info, end_info):
                    case (None, None):
                        pass

                    case (None, tuple(end_info)):
                        date_range = DateRange(
                            left=end_info[0],
                            width=-(5 / total_days) * 100,
                            start_time=None,
                            end_time=end_info[1],
                        )

                    case (tuple(start_info), None):
                        date_range = DateRange(
                            left=start_info[0],
                            width=(5 / total_days) * 100,
                            start_time=start_info[1],
                            end_time=None,
                        )

                    case (tuple(start_info), tuple(end_info)):
                        start_left = start_info[0]
                        end_left = end_info[0]
                        width = end_left - start_left
                        date_range = DateRange(
                            left=start_left,
                            width=width,
                            start_time=start_info[1],
                            end_time=end_info[1],
                        )

                task_renders.append(
                    TaskRender(
                        id=task_data.id,
                        date_range=date_range,
                    )
                )

            all_dates = [
                datetime.fromtimestamp(x.start_date)
                for x in map(
                    lambda x: data.tasks_by_id[x],
                    milestone.task_ids,
                )
                if x.start_date is not None
            ] + [
                datetime.fromtimestamp(x.end_date)
                for x in map(
                    lambda x: data.tasks_by_id[x],
                    milestone.task_ids,
                )
                if x.end_date is not None
            ]

            if len(all_dates) == 0:
                milestone_renders.append(
                    MilestoneRender(
                        id=milestone.id,
                        tasks=task_renders,
                        date_range=None,
                    )
                )

            else:
                start = min(all_dates)
                end = max(all_dates)

                left = ((start - first_month).days / total_days) * 100
                right = ((end - first_month).days / total_days) * 100

                width = right - left

                milestone_renders.append(
                    MilestoneRender(
                        id=milestone.id,
                        tasks=task_renders,
                        date_range=DateRange(
                            left=left,
                            width=width,
                            start_time=datetime.strftime(start, "%Y-%m-%d"),
                            end_time=datetime.strftime(end, "%Y-%m-%d"),
                        ),
                    )
                )

        return milestone_renders


def render_month_headers():
    """Render the month headers dynamically."""
    return rx.hstack(
        rx.foreach(
            TimelineState.all_month_ranges,  # type: ignore
            lambda month: month_header(
                month.string,
                width=f"{month.day_count * 10}px",  # type: ignore
            ),
        ),
        spacing="0",
        width=f"{TimelineState.total_width_pixels}px",
    )


def render_task_name():
    """Render the milestone names and their tasks (when expanded)."""

    def render_milestone_name(milestone: MilestoneData) -> rx.Component:
        is_expanded = TimelineState.expanded_milestones[milestone.id]
        data: ProjectData = ProjectState.data  # type: ignore

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
                    milestone.name,
                    color="#eee",
                    font_size="14px",
                    font_weight="bold",
                ),
                # a + button to create a new task under the milestone
                create_task_dialog(),
                spacing="2",
                align_items="center",
                width="100%",
                height="40px",
                min_height="40px",
            ),
            rx.cond(
                is_expanded,
                rx.foreach(
                    milestone.task_ids,
                    lambda task_id: rx.box(
                        rx.hstack(
                            task_dialog(
                                trigger=rx.hstack(
                                    rx.box(
                                        width="12px",
                                        height="12px",
                                        background_color=get_status_color(
                                            data.statuses_by_id[
                                                data.tasks_by_id[
                                                    task_id
                                                ].status_id
                                            ].name
                                        ),
                                        border_radius="2px",
                                    ),
                                    rx.text(
                                        data.tasks_by_id[task_id].name,
                                        color="#eee",
                                        font_size="14px",
                                        font_weight="medium",
                                    ),
                                ),
                                task_id=task_id,
                            ),
                            spacing="2",
                            align_items="center",
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
            ProjectState.milestones,
            render_milestone_name,
        ),
    )


def render_tasks():
    """Render the milestone rows with timeline bars (collapsed or expanded)."""

    def render_milestone_row(milestone: MilestoneRender) -> rx.Component:
        is_expanded = TimelineState.expanded_milestones[milestone.id]
        return rx.vstack(
            rx.hstack(
                rx.box(
                    # timeline bar
                    rx.cond(
                        milestone.date_range,
                        rx.box(
                            position="absolute",
                            left=f"{milestone.date_range.left}%",  # type: ignore
                            width=f"{milestone.date_range.width}%",  # type: ignore
                            height="20px",
                            background_color="#5b279c",
                            border_radius="3px",
                            border="1px solid white",
                            padding_y="0.5rem",
                        ),
                    ),
                    position="relative",
                    height="100%",
                    width=f"{TimelineState.total_width_pixels}px",
                ),
                width="100%",
                padding_y="0.5rem",
                border_bottom=rx.cond(
                    is_expanded, "none", "1px solid #4d4d4d"
                ),
                height="41px",
            ),
            rx.cond(
                is_expanded,
                rx.foreach(
                    milestone.tasks,
                    lambda task: task_row(task),
                ),
            ),
            spacing="0",
            width="100%",
        )

    return rx.fragment(
        rx.box(
            rx.foreach(
                TimelineState.render_milestone,  # type: ignore
                render_milestone_row,
            ),
            width="100%",
            min_width=f"{TimelineState.total_width_pixels}px",  # Ensure the tasks area matches the headers
        )
    )


@rx.page(route="project/timeline/[project_id]")
@protected_page_with(
    on_signed_in=[ProjectState.load_project, TimelineState.on_mount]
)
def timeline_view() -> rx.Component:
    return base.base_page(
        rx.skeleton(
            rx.fragment(
                rx.text(
                    "Project Timeline", class_name="text-3xl font-bold mb-20"
                ),
                rx.flex(
                    rx.box(
                        render_task_name(),
                        # Create new milestone button in the last row
                        create_milestone_dialog(
                            trigger=rx.button(
                                rx.icon(tag="plus"),
                                rx.text("Create New Milestone"),
                            )
                        ),
                        width="400px",
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
                            spacing="0",
                            width=f"{TimelineState.total_width_pixels}px",
                        ),
                        height="auto",
                        overflow_x="auto",
                        scrollbars="horizontal",
                    ),
                    direction="row",
                    width="100%",
                    spacing="0",
                    height="auto",
                ),
                width="100%",
                spacing="5",
                margin="auto",
                padding="20",
                border="1px solid #ddd",
                border_radius="5",
            ),
            loading=~ProjectState.loaded,
        )
    )


class TooltipState(rx.State):
    """State for the tooltip component."""

    visible: bool = False
    hovered_task_id: int | None = None

    def show_tooltip(self, task_id: int) -> None:
        self.visible = True
        self.hovered_task_id = task_id

    def hide_tooltip(self) -> None:
        self.visible = False
        self.hovered_task_id = None


def get_status_color(status: str):
    """Return color based on status."""
    # if status == "DONE":
    #     return "#4caf50"
    # elif status == "IN PROGRESS":
    #     return "#a881e6"
    # else:
    return "#e0e0e0"


def month_header(month: str, width: str) -> rx.Component:
    """Month header box."""
    return rx.box(
        rx.text(month, font_size="14px", weight="bold"),
        width=width,
        flex="0 0 auto",
        text_align="center",
        background_color="#303030",
        padding_y="0.5rem",
        border_right="1px solid #4d4d4d",
    )


def task_box(task: TaskRender, date_range: DateRange):
    start_pos = date_range.left
    end_pos = date_range.left + date_range.width

    # Calculate the width of the task bar
    width_percent = rx.cond(
        end_pos >= start_pos,
        end_pos - start_pos,
        0,
    )
    start_percent = start_pos

    # Positioning for start label
    start_label_left = rx.cond(
        start_pos < 5,  # If the start is near the left edge
        "0%",
        f"{start_percent}%",
    )
    start_label_transform = rx.cond(
        start_pos < 5,
        "translateX(0%)",  # No transform if near the left edge
        "translateX(-100%)",  # Move left so the right edge of the label aligns with the bar's start
    )

    # Positioning for end label
    end_label_left = rx.cond(
        end_pos > 95,  # If the end is near the right edge
        "100%",
        f"{end_pos}%",
    )
    end_label_transform = rx.cond(
        end_pos > 95,
        "translateX(-100%)",  # Move left so the label stays within bounds
        "translateX(0%)",  # No transform, so the left edge of the label aligns with the bar's end
    )

    # Align labels vertically with the bar
    label_top = "0px"  # Align with the top of the bar
    label_height = "20px"  # Match the bar height
    label_line_height = "20px"  # Center the text vertically within the label

    # For short tasks, adjust positioning to prevent overlap
    start_label_left_adjusted = rx.cond(
        (end_pos - start_pos) < 10,  # If the task is very short
        f"{start_percent}%",  # Keep it at the start
        start_label_left,
    )
    end_label_left_adjusted = rx.cond(
        (end_pos - start_pos) < 10,
        f"{end_pos}%",  # Keep it at the end
        end_label_left,
    )

    # Ensure labels are aligned properly with the bar's edges
    start_label_text_align = rx.cond(
        start_pos < 5,
        "left",  # Align left if near the left edge
        "right",  # Align right so the label's right edge is flush with the bar's start
    )
    end_label_text_align = rx.cond(
        end_pos > 95,
        "right",  # Align right if near the right edge
        "left",  # Align left so the label's left edge is flush with the bar's end
    )

    return rx.box(
        # Start date label
        rx.cond(
            date_range.start_time,
            rx.text(
                date_range.start_time,
                color="#eee",
                font_size="12px",
                font_weight="medium",
                padding="0.25rem 0.5rem",
                background_color="#333",
                border_radius="3px",
                position="absolute",
                top=label_top,  # Align with the top of the bar
                height=label_height,  # Match the bar height
                line_height=label_line_height,  # Center text vertically
                left=start_label_left_adjusted,
                transform=start_label_transform,
                text_align=start_label_text_align,
                white_space="nowrap",
                display=rx.cond(
                    (TooltipState.visible)
                    & (TooltipState.hovered_task_id == task.id),
                    "block",
                    "none",
                ),
            ),
        ),
        # End date label
        rx.cond(
            date_range.end_time,
            rx.text(
                date_range.end_time,
                color="#eee",
                font_size="12px",
                font_weight="medium",
                padding="0.25rem 0.5rem",
                background_color="#333",
                border_radius="3px",
                position="absolute",
                top=label_top,  # Align with the top of the bar
                height=label_height,  # Match the bar height
                line_height=label_line_height,  # Center text vertically
                left=end_label_left_adjusted,
                transform=end_label_transform,
                text_align=end_label_text_align,
                white_space="nowrap",
                display=rx.cond(
                    (TooltipState.visible)
                    & (TooltipState.hovered_task_id == task.id),
                    "block",
                    "none",
                ),
            ),
        ),
        on_mouse_over=lambda: TooltipState.show_tooltip(
            task.id
        ),  # type:ignore
        on_mouse_out=TooltipState.hide_tooltip,  # type:ignore
        position="absolute",
        left=f"{start_percent}%",
        height="20px",
        width=f"{width_percent}%",
        background_color="#5b279c",
        border_radius="3px",
    )


def task_row(task: TaskRender) -> rx.Component:

    return rx.hstack(
        rx.box(
            rx.cond(
                task.date_range,
                task_box(task, task.date_range),  # type: ignore
            ),
            position="relative",
            height="40px",
            width="100%",
        ),
        width="100%",
        padding_y="0.5rem",
        border_bottom="1px solid #4d4d4d",
        height="40px",
    )


def task_name(task: Dict[str, Any]) -> rx.Component:
    """Task name box."""
    status_color = get_status_color(str(task["status"]))

    return rx.box(
        rx.hstack(
            rx.box(
                width="12px",
                height="12px",
                background_color=status_color,
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
        ),
        width="100%",
        padding="0.5rem",
        border_bottom="1px solid #4d4d4d",
        height="40px",  # Fixed height to match timeline rows
    )
