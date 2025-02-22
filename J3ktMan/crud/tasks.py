import reflex as rx
from sqlmodel import Session
from sqlalchemy import delete
from ..model.tasks import (
    Task,
    TaskAssignment,
    TaskDependency,
    Milestone,
    Priority,
)

import datetime
from typing import Sequence


class ExistingMilestoneNameError(Exception):
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
            name=MilestoneCreate.name,
            description=MilestoneCreate.description,
            project_id=MilestoneCreate.parent_project_id,
            due_date=current_time,
        )
        session.add(milestone)
        session.commit()
        session.refresh(milestone)

        return milestone


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
    name: str, description: str, parent_milestone_id: int, priority: Priority
) -> Task:
    """
    Creates a task in the given milestone ID.

    Chechs:
    - If there's a task with the same name in the same milestone
    """
    ...


def get_task_by_id(task_id: int) -> Task:
    """
    Returns a task by its ID
    """

    ...


def delete_task(task_id: int) -> None:
    """
    Deletes a task by its ID

    Chechs:
    - Deletes all task assignments related to the task
    - Removes the **dependency** of the task from other tasks
    """

    ...


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

    ...


def get_assigned_tasks_by_user_id(user_id: str) -> list[Task]:
    """
    Returns all tasks assigned to the user.
    """
    ...


def get_assignees_by_task_id(task_id: int) -> list[str]:
    """
    Returns all user IDs assigned to the task.
    """
    ...


def unassign_task(task_id: int, user_id: str) -> None:
    """
    Unassigns a task from a user.

    Chechs:
    - If the task is not assigned to the user
    """
    ...


def create_task_dependency(
    dependent_task_id: int, dependency_task_id: int
) -> TaskDependency:
    """
    Creates a dependency between two tasks.

    Chechs:
    - Error on cyclic dependencies
    """

    ...


def remove_task_dependency(
    dependent_task_id: int, dependency_task_id: int
) -> None:
    """
    Removes a dependency between two tasks.
    """
