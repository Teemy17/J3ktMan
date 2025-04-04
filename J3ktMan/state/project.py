import reflex_clerk as clerk
import reflex as rx

from reflex.event import EventSpec

from J3ktMan.crud.project import (
    InvalidProjectIDError,
    get_project,
    is_in_project,
)
from J3ktMan.crud.tasks import (
    ExistingMilestoneNameError,
    ExistingStatusNameError,
    ExistingTaskNameError,
    MilestoneCreate,
    DateError,
    assign_milestone,
    create_milestone,
    create_status,
    create_task,
    delete_status,
    delete_task,
    get_milestones_by_project_id,
    get_statuses_by_project_id,
    get_tasks_by_status_id,
    rename_status,
    rename_task,
    set_status,
    set_task_description,
    update_task_dates,
)
from J3ktMan.model.tasks import Priority


class Task(rx.Base):
    id: int
    name: str
    description: str
    status_id: int
    milestone_id: int | None
    start_date: int | None
    end_date: int | None


class Status(rx.Base):
    id: int
    name: str
    description: str
    task_ids: list[int]


class Milestone(rx.Base):
    id: int
    name: str
    description: str
    task_ids: list[int]


class Data(rx.Base):
    project_id: int
    project_name: str
    milestones_by_id: dict[int, Milestone]
    tasks_by_id: dict[int, Task]
    statuses_by_id: dict[int, Status]


class State(rx.State):
    """
    This state fetches all the data needed to display the project page. It was
    meant to be used in pages that uses the project information.
    """

    data: Data | None

    @rx.event
    async def load_project(self) -> None | list[EventSpec]:
        """
        Invokes this once before the page is loaded to load the project data.
        """
        self.reset()

        milestones_by_id: dict[int, Milestone] = {}
        tasks_by_id: dict[int, Task] = {}
        statuses_by_id: dict[int, Status] = {}

        clerk_state = await self.get_state(clerk.ClerkState)
        if clerk_state.user_id is None:
            return

        try:
            project_id = int(self.router.page.params["project_id"])
            project = get_project(project_id)

            if not is_in_project(clerk_state.user_id, project_id):
                return [
                    rx.toast.error(
                        "You are not authorized to view this project",
                        position="top-center",
                    ),
                ]

            milestones = get_milestones_by_project_id(project_id)
            for milestone in milestones:
                milestones_by_id[milestone.id] = Milestone(
                    id=milestone.id,
                    name=milestone.name,
                    description=milestone.description,
                    task_ids=[],
                )

            statuses = get_statuses_by_project_id(project_id)
            for status in statuses:
                statuses_by_id[status.id] = Status(
                    id=status.id,
                    name=status.name,
                    description=status.description,
                    task_ids=[],
                )

                tasks = get_tasks_by_status_id(status.id)

                for task in tasks:
                    tasks_by_id[task.id] = Task(
                        id=task.id,
                        name=task.name,
                        description=task.description,
                        status_id=task.status_id,
                        milestone_id=task.milestone_id,
                        start_date=task.start_date,
                        end_date=task.end_date,
                    )

                    statuses_by_id[status.id].task_ids.append(task.id)

                    if task.milestone_id is not None:
                        milestones_by_id[task.milestone_id].task_ids.append(
                            task.id
                        )

            new_page_data = Data(
                project_id=project_id,
                project_name=project.name,
                milestones_by_id=milestones_by_id,
                tasks_by_id=tasks_by_id,
                statuses_by_id=statuses_by_id,
            )

            self.data = new_page_data

        except (KeyError, ValueError, InvalidProjectIDError):
            return [
                rx.redirect("/"),
                rx.toast.error(
                    "Invalid project ID, Please try again",
                    position="top-center",
                ),
            ]

    @rx.var
    def loaded(self) -> bool:
        """
        Returns True if the project data has been loaded.
        """

        return self.data is not None

    @rx.var(cache=True)
    def milestone_name_by_ids(self) -> dict[int, str]:
        if self.data is None:
            return {}

        result = {}
        for id, mil in self.data.milestones_by_id.items():
            result[id] = mil.name

        return result

    @rx.var(cache=True)
    def milestones(self) -> list[Milestone]:
        """
        Returns the list of milestones.
        """

        if self.data is None:
            return []

        return list(self.data.milestones_by_id.values())

    @rx.var(cache=True)
    def statuses(self) -> list[Status]:
        """
        Returns the list of statuses.
        """

        if self.data is None:
            return []

        return list(self.data.statuses_by_id.values())

    def tasks(self) -> dict[int, Task]:
        """
        Returns the dict of tasks.
        """

        if self.data is None:
            return {}

        return self.data.tasks_by_id

    @rx.event
    def create_status(self, status_name: str) -> list[EventSpec] | None:
        if self.data is None:
            return

        try:
            status = create_status(status_name, "", self.data.project_id)

            self.data.statuses_by_id[status.id] = Status(
                id=status.id,
                name=status.name,
                description=status.description,
                task_ids=[],
            )

            return [
                rx.toast.success(
                    f"Status {status_name} has been created",
                    position="top-center",
                )
            ]

        except ExistingStatusNameError:
            return [
                rx.toast.error(
                    f"Status {status_name} already exists",
                    position="top-center",
                )
            ]

    @rx.event
    def create_task(
        self,
        name: str,
        description: str,
        priority: Priority,
        status_id: int,
        milestone_id: int | None,
        start_date: int | None = None,
        end_date: int | None = None,
    ) -> list[EventSpec] | None:

        if self.data is None:
            return

        try:
            # create task
            task = create_task(
                name,
                description,
                priority,
                status_id,
                milestone_id,
                start_date,
                end_date,
            )

            self.data.tasks_by_id[task.id] = Task(
                id=task.id,
                name=task.name,
                description=task.description,
                status_id=task.status_id,
                milestone_id=None,
                start_date=task.start_date,
                end_date=task.end_date,
            )
            self.data.statuses_by_id[status_id].task_ids.append(task.id)

            return [
                rx.toast.success(
                    f'Task "{name}" has been created',
                    position="top-center",
                )
            ]

        except ExistingTaskNameError:
            return [
                rx.toast.error(
                    f'Task "{name}" already exists',
                    position="top-center",
                )
            ]

        except DateError:
            return [
                rx.toast.error(
                    "Invalid date range",
                    position="top-center",
                )
            ]

    @rx.event
    def rename_status(
        self, status_id: int, new_name: str
    ) -> list[EventSpec] | None:
        if self.data is None:
            return

        try:
            status = rename_status(status_id, new_name)
            self.data.statuses_by_id[status.id].name = status.name

            return [
                rx.toast.success(
                    f'Status "{new_name}" has been renamed',
                    position="top-center",
                )
            ]

        except ExistingStatusNameError:
            return [
                rx.toast.error(
                    f'Status "{new_name}" already exists',
                    position="top-center",
                )
            ]

    @rx.event
    def set_task_status(
        self,
        task_id: int,
        status_id: int,
    ) -> list[EventSpec] | None:
        if self.data is None:
            return

        previous_status_id = set_status(task_id, status_id)

        self.data.statuses_by_id[previous_status_id].task_ids.remove(task_id)
        self.data.statuses_by_id[status_id].task_ids.append(task_id)
        self.data.tasks_by_id[task_id].status_id = status_id

    @rx.event
    def create_milestone(
        self, name: str, description: str
    ) -> list[EventSpec] | None:
        if self.data is None:
            return

        try:
            milestone = create_milestone(
                MilestoneCreate(
                    name=name,
                    description=description,
                    parent_project_id=self.data.project_id,
                )
            )

            self.data.milestones_by_id[milestone.id] = Milestone(
                id=milestone.id,
                name=milestone.name,
                description=milestone.description,
                task_ids=[],
            )

            return [
                rx.toast.success(
                    f'Milestone "{name}" has been created',
                    position="top-center",
                )
            ]

        except ExistingMilestoneNameError:
            return [
                rx.toast.error(
                    f'Milestone "{name}" already exists',
                    position="top-center",
                )
            ]

    @rx.event
    def delete_status(
        self, status_id: int, migration_status_id: int
    ) -> list[EventSpec] | None:
        if self.data is None:
            return None

        # delete status
        affecting_tasks = delete_status(status_id, migration_status_id)

        # remove status from state
        deleted_status_name = self.data.statuses_by_id[status_id].name
        del self.data.statuses_by_id[status_id]

        # remove tasks from state
        for affecting_task in affecting_tasks:
            self.data.tasks_by_id[affecting_task.id].model = affecting_task

            self.data.statuses_by_id[migration_status_id].task_ids.append(
                affecting_task.id
            )

        return [
            rx.toast.success(
                f"Status {deleted_status_name} has been deleted",
                position="top-center",
            )
        ]

    @rx.event
    def assign_milestone(
        self, task_id: int, milestone_id: int | None
    ) -> list[EventSpec] | None:
        if self.data is None:
            return

        old_milestone_id = self.data.tasks_by_id[task_id].milestone_id
        assign_milestone(milestone_id, task_id)

        # update task in state

        if old_milestone_id is not None:
            self.data.milestones_by_id[old_milestone_id].task_ids.remove(
                task_id
            )

        self.data.tasks_by_id[task_id].milestone_id = milestone_id

        if milestone_id is not None:
            self.data.milestones_by_id[milestone_id].task_ids.append(task_id)

        task_name = self.data.tasks_by_id[task_id].name

        message = (
            f'Task "{task_name}" has been assigned to "{self.data.milestones_by_id[milestone_id].name}"'  # type: ignore
            if milestone_id is not None
            else f'Task "{task_name}" has been unassigned'
        )

        return [
            rx.toast.success(message, position="top-center"),
        ]

    @rx.event
    def delete_task(self, task_id: int) -> list[EventSpec] | None:
        if self.data is None:
            return

        delete_task(task_id)

        # delete task
        deleted_task = self.data.tasks_by_id[task_id]
        del self.data.tasks_by_id[task_id]

        # remove task from status
        self.data.statuses_by_id[deleted_task.status_id].task_ids.remove(
            deleted_task.id
        )

        return [
            rx.toast.success(
                f'Task "{deleted_task.name}" has been deleted',
                position="top-center",
            )
        ]

    @rx.event
    def rename_task(
        self, task_id: int, new_name: str
    ) -> list[EventSpec] | None:
        if self.data is None:
            return

        try:
            new_task_model = rename_task(task_id, new_name)
            self.data.tasks_by_id[task_id].name = new_task_model.name

            return [
                rx.toast.success(
                    f'Task renamed to "{new_name}" successfully',
                    position="top-center",
                )
            ]

        except ExistingTaskNameError:
            return [
                rx.toast.error(
                    f'Task with name"{new_name}" already exists',
                    position="top-center",
                )
            ]

    @rx.event
    def set_task_description(
        self, task_id: int, new_description: str
    ) -> list[EventSpec] | None:
        if self.data is None:
            return

        set_task_description(task_id, new_description)
        task = self.data.tasks_by_id[task_id]
        task.description = new_description

        return [
            rx.toast.success(
                f'Task "{task.name}" description has been updated',
                position="top-center",
            )
        ]

    @rx.event
    def change_task_dates(
        self,
        task_id: int,
        start_date: int | None = None,
        end_date: int | None = None,
    ) -> list[EventSpec] | None:
        if self.data is None:
            return
        try:
            update_task_dates(task_id, start_date, end_date)
            task = self.data.tasks_by_id[task_id]
            task.start_date = start_date
            task.end_date = end_date

            return [
                rx.toast.success(
                    f'Task "{task.name}" dates have been updated',
                    position="top-center",
                )
            ]
        except DateError:
            return [
                rx.toast.error(
                    "Invalid date range",
                    position="top-center",
                )
            ]

    @rx.event
    def edit_task(
        self,
        task_id: int,
        name: str,
        description: str,
        start_date: int | None = None,
        end_date: int | None = None,
    ) -> list[EventSpec] | None:
        if self.data is None:
            return

        try:
            task = rename_task(task_id, name)
            task.description = description
            update_task_dates(task_id, start_date, end_date)
            self.data.tasks_by_id[task_id].name = task.name
            self.data.tasks_by_id[task_id].description = task.description
            self.data.tasks_by_id[task_id].start_date = start_date
            self.data.tasks_by_id[task_id].end_date = end_date

            return [
                rx.toast.success(
                    f'Task "{name}" has been updated',
                    position="top-center",
                )
            ]
        except ExistingTaskNameError:
            return [
                rx.toast.error(
                    f'Task with name"{name}" already exists',
                    position="top-center",
                )
            ]
