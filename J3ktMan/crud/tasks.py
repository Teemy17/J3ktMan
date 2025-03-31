import reflex as rx

from ..model.tasks import (
    Task,
    Status,
    TaskAssignment,
    TaskDependency,
    Milestone,
    Priority,
)

import datetime
from typing import Sequence


class ExistingMilestoneNameError(Exception):
    pass


class ExistingTaskNameError(Exception):
    pass


class TaskAlreadyAssignedError(Exception):
    pass


class CyclicDependencyError(Exception):
    pass


class MilestoneAlreadyAssignedError(Exception):
    pass


class MilestoneCreate(rx.Base):
    name: str
    description: str
    parent_project_id: int


def create_milestone(info: MilestoneCreate) -> Milestone:
    """
    Creates a milestone in the given project ID.
    """
    with rx.session() as session:
        current_time = int(datetime.datetime.now().timestamp())

        # check if there's a milestone with the same name
        existing_milestone = session.exec(
            Milestone.select().where(
                (Milestone.name == info.name)
                & (Milestone.project_id == info.parent_project_id)
            )
        ).first()

        if existing_milestone is not None:
            raise ExistingMilestoneNameError()

        milestone = Milestone(
            name=info.name,
            description=info.description,
            project_id=info.parent_project_id,
            due_date=current_time,
        )
        session.add(milestone)
        session.commit()
        session.refresh(milestone)

        return milestone


def get_milestone_by_task_id(task_id: int) -> Milestone | None:
    """
    Returns the milestone of a task.
    """
    with rx.session() as session:
        task = session.exec(Task.select().where(Task.id == task_id)).first()
        if task is None:
            raise InvalidTaskIDError()

        return session.exec(
            Milestone.select().where(Milestone.id == task.milestone_id)
        ).first()


def set_task_description(task_id: int, new_description: str) -> Task:
    with rx.session() as session:
        task = session.exec(Task.select().where(Task.id == task_id)).first()
        if task is None:
            raise InvalidTaskIDError()

        task.description = new_description
        session.add(task)
        session.commit()
        session.refresh(task)

    return task


def rename_status(status_id: int, new_name: str) -> Status:
    with rx.session() as session:
        status = session.exec(
            Status.select().where(Status.id == status_id)
        ).first()

        if status is None:
            raise InvalidStatusIDError()

        # check if there's a status with the same name in the same project
        existing_status = session.exec(
            Status.select().where(
                (Status.name == new_name)
                & (Status.project_id == status.project_id)
            )
        ).first()

        if existing_status is not None:
            raise ExistingStatusNameError()

        status.name = new_name
        session.add(status)
        session.commit()
        session.refresh(status)

        return status


def rename_task(task_id: int, new_name: str) -> Task:
    with rx.session() as session:
        task = session.exec(Task.select().where(Task.id == task_id)).first()

        if task is None:
            raise InvalidTaskIDError()

        parent_status = session.exec(
            Status.select().where(Status.id == task.status_id)
        ).first()

        assert parent_status is not None

        # check if there's a task with the same name in the same project
        existing_task = session.exec(
            Task.select()
            .join(Status)
            .where(
                (Task.name == new_name)
                & (Status.project_id == parent_status.project_id)
            )
        ).first()

        if existing_task is not None:
            raise ExistingTaskNameError()

        task.name = new_name
        session.add(task)
        session.commit()
        session.refresh(task)

        return task


def get_milestones_by_project_id(project_id: int) -> Sequence[Milestone]:
    """
    Returns all milestones in the given project ID.
    """
    with rx.session() as session:
        return session.exec(
            Milestone.select().where(Milestone.project_id == project_id)
        ).all()


def get_milestone_by_id(milestone_id: int) -> Milestone | None:
    """
    Returns a milestone by its ID.
    """
    with rx.session() as session:
        return session.exec(
            Milestone.select().where(Milestone.id == milestone_id)
        ).first()


def assign_milestone(milestone_id: int | None, task_id: int) -> Task | None:
    """
    Assign a milestone to an existing task.
    """
    with rx.session() as session:

        task = session.exec(Task.select().where(Task.id == task_id)).first()
        if task is None:
            raise InvalidTaskIDError()

        if milestone_id is not None:
            milestone = get_milestone_by_id(milestone_id)
            if milestone is None:
                raise InvalidMilestoneIDError()

        task.milestone_id = milestone_id
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


def delete_milestone(milestone_id: int) -> None:
    """
    Deletes a milestone by its ID.

    Chechs:
    - Deletes all tasks in the milestone
    """
    with rx.session() as session:
        milestone = get_milestone_by_id(milestone_id)
        if milestone is None:
            return

        # get all tasks in the milestone
        tasks = get_tasks_by_milestone_id(milestone_id)

        # delete all tasks in the milestone
        for task in tasks:
            session.delete(task)

        session.delete(milestone)
        session.commit()


def create_task(
    name: str,
    description: str,
    priority: Priority,
    status_id: int,
) -> Task:
    """
    Creates a task in the given milestone ID.

    Chechs:
    - If there's a task with the same name in the same milestone
    """
    with rx.session() as session:
        status = session.exec(
            Status.select().where(Status.id == status_id)
        ).first()

        if status is None:
            raise InvalidStatusIDError()

        project_id = status.project_id

        # should have no same task name in the same project

        task = session.exec(
            Task.select()
            .join(Status)
            .where((Task.name == name) & (Status.project_id == project_id))
        ).first()

        if task is not None:
            raise ExistingTaskNameError()

        new_task = Task(
            name=name,
            description=description,
            milestone_id=None,
            priority=priority,
            status_id=status_id,
        )

        session.add(new_task)
        session.commit()

        session.refresh(new_task)

        return new_task


def get_task_by_id(task_id: int) -> Task | None:
    """
    Returns a task by its ID
    """
    with rx.session() as session:
        return session.exec(Task.select().where(Task.id == task_id)).first()


def delete_task(task_id: int) -> None:
    """
    Deletes a task by its ID

    Chechs:
    - Deletes all task assignments related to the task
    - Removes the **dependency** of the task from other tasks
    """
    with rx.session() as session:
        task = get_task_by_id(task_id)
        if task is None:
            return

        assignments = session.exec(
            TaskAssignment.select().where((TaskAssignment.task_id == task_id))
        ).all()

        for assignment in assignments:
            session.delete(assignment)

        dependencies = session.exec(
            TaskDependency.select().where(
                (TaskDependency.dependency_id == task_id)
                | (TaskDependency.dependant_id == task_id)
            )
        ).all()

        for dependency in dependencies:
            session.delete(dependency)

        session.delete(task)
        session.commit()


def get_tasks_by_milestone_id(milestone_id: int) -> Sequence[Task]:
    """
    Returns all tasks in the given milestone ID.
    """
    with rx.session() as session:
        return session.exec(
            Task.select().where(Task.milestone_id == milestone_id)
        ).all()


def assign_task(task_id: int, user_id: str) -> TaskAssignment:
    """
    Assigns a task to a user.

    Chechs:
    - If the task is already assigned to the user
    """
    with rx.session() as session:
        current_time = int(datetime.datetime.now().timestamp())

        # check if the task is already assigned to the user
        existing_assignment = session.exec(
            TaskAssignment.select().where(
                (TaskAssignment.task_id == task_id)
                & (TaskAssignment.user_id == user_id)
            )
        ).first()

        if existing_assignment is not None:
            raise TaskAlreadyAssignedError()

        assignment = TaskAssignment(
            task_id=task_id,
            user_id=user_id,
            assigned_at=current_time,
        )
        session.add(assignment)
        session.commit()
        session.refresh(assignment)

        return assignment


def get_assigned_tasks_by_user_id(user_id: str) -> Sequence[Task]:
    """
    Returns all tasks assigned to the user.
    """
    with rx.session() as session:
        return session.exec(
            Task.select()
            .join(TaskAssignment)
            .where(TaskAssignment.user_id == user_id)
        ).all()


def get_assignees_by_task_id(task_id: int) -> Sequence[str]:
    """
    Returns all user IDs assigned to the task.
    """
    with rx.session() as session:
        task_assignments = session.exec(
            TaskAssignment.select().where(TaskAssignment.task_id == task_id)
        ).all()

        return [task.user_id for task in task_assignments]


def unassign_task(task_id: int, user_id: str) -> None:
    """
    Unassigns a task from a user.

    Chechs:
    - If the task is not assigned to the user
    """
    with rx.session() as session:
        assigned_task = session.exec(
            TaskAssignment.select().where(
                (TaskAssignment.task_id == task_id)
                & (TaskAssignment.user_id == user_id)
            )
        ).first()

        if assigned_task is None:
            return

        session.delete(assigned_task)
        session.commit()


def create_task_dependency(
    dependent_task_id: int, dependency_task_id: int
) -> TaskDependency:
    """
    Creates a dependency between two tasks.

    Chechs:
    - Error on cyclic dependencies
    """
    with rx.session() as session:
        # check if there's a cyclic dependency
        cyclic_dependency = session.exec(
            TaskDependency.select().where(
                (TaskDependency.dependency_id == dependent_task_id)
                & (TaskDependency.dependant_id == dependency_task_id)
            )
        ).first()

        if cyclic_dependency is not None:
            raise CyclicDependencyError()

        dependency = TaskDependency(
            dependency_id=dependency_task_id,
            dependant_id=dependent_task_id,
        )
        session.add(dependency)
        session.commit()
        session.refresh(dependency)

        return dependency


def remove_task_dependency(
    dependent_task_id: int, dependency_task_id: int
) -> None:
    """
    Removes a dependency between two tasks.
    """
    with rx.session() as session:
        dependency = session.exec(
            TaskDependency.select().where(
                (TaskDependency.dependency_id == dependent_task_id)
                & (TaskDependency.dependant_id == dependency_task_id)
            )
        ).first()

        if dependency is None:
            return

        session.delete(dependency)
        session.commit()


class ExistingStatusNameError(Exception):
    pass


def create_status(name: str, description: str, project_id: int) -> Status:
    """
    Creates a status in the given project ID.
    """
    with rx.session() as session:
        # check if there's exist a status with the same name
        existing_status = session.exec(
            Status.select().where(
                (Status.name == name) & (Status.project_id == project_id)
            )
        ).first()

        if existing_status is not None:
            raise ExistingStatusNameError()

        status = Status(
            name=name,
            description=description,
            project_id=project_id,
        )

        session.add(status)
        session.commit()
        session.refresh(status)

        return status


def get_statuses_by_project_id(project_id: int) -> Sequence[Status]:
    """
    Returns all statuses in the given project ID.
    """
    with rx.session() as session:
        return session.exec(
            Status.select().where(Status.project_id == project_id)
        ).all()


def get_tasks_by_status_id(status_id: int) -> Sequence[Task]:
    """
    Returns all tasks in the given status ID.
    """
    with rx.session() as session:
        return session.exec(
            Task.select().where(Task.status_id == status_id)
        ).all()


class InvalidTaskIDError(Exception):
    pass


class InvalidStatusIDError(Exception):
    pass


class InvalidMilestoneIDError(Exception):
    pass


def set_status(task_id: int, status_id: int) -> int:
    with rx.session() as session:
        # check if the task and status exist in the same project
        task = session.exec(Task.select().where(Task.id == task_id)).first()
        status = session.exec(
            Status.select().where(Status.id == status_id)
        ).first()

        if task is None:
            raise InvalidTaskIDError()

        if status is None:
            raise InvalidStatusIDError()

        previous_status_id = task.status_id
        task.status_id = status_id

        session.commit()

        return previous_status_id


def delete_status(status_id: int, to_status_id: int) -> Sequence[Task]:
    """
    Deletes a status by its ID.

    Chechs:
    - Moves all tasks in the status to the given status ID
    """
    with rx.session() as session:
        status = session.exec(
            Status.select().where(Status.id == status_id)
        ).first()

        if status is None:
            raise InvalidStatusIDError()

        # get all tasks in the status
        tasks = session.exec(
            Task.select().where(Task.status_id == status_id)
        ).all()

        # move all tasks in the status to the given status ID
        for task in tasks:
            task.status_id = to_status_id
            session.add(task)

        session.delete(status)
        session.commit()

        for task in tasks:
            session.refresh(task)

        return tasks
