from enum import StrEnum, unique

import sqlalchemy
import sqlmodel as sql
import reflex as rx


@unique
class Priority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Milestone(rx.Model, table=True):
    """
    Milestones to add to a project sprints.
    """

    id: int = sql.Field(primary_key=True, nullable=False)  # type:ignore

    project_id: int = sql.Field(foreign_key="project.id", nullable=False)
    """
    Project's id that the milestone belongs to.
    """

    name: str
    """
    Name of the milestone.
    """

    description: str
    """
    Description of the milestone.
    """

    due_date: int
    """
    Unix epoch timestamp of when the milestone is due.
    """


class Task(rx.Model, table=True):
    """
    Represents a task in a project.
    """

    id: int = sql.Field(primary_key=True, nullable=False)  # type:ignore

    milestone_id: int = sql.Field(foreign_key="milestone.id", nullable=False)
    """
    Milestone's id that the task belongs to.
    """

    status_id: int = sql.Field(foreign_key="status.id", nullable=False)
    """
    Status id of the task.
    """

    priority: Priority = sql.Field(
        sa_column=sql.Column(
            "priority",
            sqlalchemy.Enum(Priority, name="priority"),
            nullable=False,
        )
    )
    """
    Priority of the task (LOW, MEDIUM, HIGH).
    """

    description: str
    """
    Description of the task.
    """


class Status(rx.Model, table=True):
    """
    Represents the status of a task.
    """

    id: int = sql.Field(primary_key=True, nullable=False)  # type:ignore

    project_id: int = sql.Field(foreign_key="project.id", nullable=False)
    """
    Project's id that the current status belongs to.
    """

    name: str
    """
    Name of the status.
    """

    description: str
    """
    Description of the status.
    """


class TaskAssignment(rx.Model, table=True):
    """
    Represents the assignment of a task to a clerk.
    """

    task_id: int = sql.Field(
        primary_key=True,
        nullable=False,
        foreign_key="task.id",
    )
    """
    Task's id that the clerk is assigned to.
    """

    user_id: str = sql.Field(
        primary_key=True,
        nullable=False,
    )
    """
    Clerk's user_id that is assigned to the task.
    """

    assigned_at: int
    """
    Unix epoch timestamp of when the task was assigned to the clerk.
    """


class TaskDependency(rx.Model, table=True):
    """
    Dependencies of tasks.
    """

    dependency_id: int = sql.Field(
        foreign_key="task.id",
        nullable=True,
    )
    """
    Task's id that the current task depends on.
    """
    dependant_id: int = sql.Field(
        foreign_key="task.id",
        nullable=True,
    )
    """
    Task's id that depends on the current task.
    """
