import reflex_clerk as clerk
import reflex as rx

from reflex.event import EventSpec

from J3ktMan.crud.project import (
    InvalidProjectIDError,
    get_project,
    is_in_project,
)
from J3ktMan.crud.tasks import (
    ExistingStatusNameError,
    ExistingTaskNameError,
    MilestoneCreate,
    create_milestone,
    create_status,
    create_task,
    delete_status,
    get_milestones_by_project_id,
    get_statuses_by_project_id,
    get_tasks_by_status_id,
    rename_status,
    set_status,
)
from J3ktMan.model.tasks import Priority


class Task(rx.Base):
    id: int
    name: str
    description: str
    status_id: int
    milestone_id: int | None


class Status(rx.Base):
    id: int
    name: str
    description: str
    task_ids: list[int]


class Milestone(rx.Base):
    id: int
    name: str
    description: str


class Data(rx.Base):
    project_id: int
    project_name: str
    milestones_by_id: dict[int, Milestone]
    tasks_by_id: dict[int, Task]
    statuses_by_id: dict[int, Status]


class State(rx.State):
    """
    This state fetches all the data needed to display the project page. It waas
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
                    )

                    statuses_by_id[status.id].task_ids.append(task.id)

            milestones = get_milestones_by_project_id(project_id)
            for milestone in milestones:
                milestones_by_id[milestone.id] = Milestone(
                    id=milestone.id,
                    name=milestone.name,
                    description=milestone.description,
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
        self, name: str, description: str, priority: Priority, status_id: int
    ) -> list[EventSpec] | None:

        if self.data is None:
            return

        try:
            # create task
            task = create_task(name, description, priority, status_id)

            self.data.tasks_by_id[task.id] = Task(
                id=task.id,
                name=task.name,
                description=task.description,
                status_id=task.status_id,
                milestone_id=None,
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
            )

            return [
                rx.toast.success(
                    f'Milestone "{name}" has been created',
                    position="top-center",
                )
            ]

        except ExistingStatusNameError:
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
