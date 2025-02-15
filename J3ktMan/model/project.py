from enum import StrEnum, unique

import sqlalchemy
import sqlmodel as sql
import reflex as rx


@unique
class Role(StrEnum):
    OWNER = "OWNER"
    COLLABORATOR = "COLLABORATOR"


class Project(rx.Model, table=True):
    """
    Project model.
    """

    id: int = sql.Field(primary_key=True, nullable=False)  # type:ignore

    name: str
    """
    Name of the project.
    """

    created_at: int
    """
    Unix epoch timestamp of when the project was created.
    """

    starting_date: int
    """
    Unix epoch timestamp of when the project started.
    """


class ProjectMember(rx.Model, table=True):
    """
    Represents a member in a project. This table doesn't include the owner of
    the project.
    """

    project_id: int = sql.Field(
        primary_key=True,
        nullable=False,
        foreign_key="project.id",
    )
    """
    Project's id that the user is a member of.
    """

    user_id: str = sql.Field(
        primary_key=True,
        nullable=False,
    )
    """
    Clerk's user_id that is a member of the project.
    """

    role: Role = sql.Field(
        sa_column=sqlalchemy.Column(
            "role", sqlalchemy.Enum(Role, name="role"), nullable=False
        ),
    )
    """
    Role of the member.
    """

    joined_at: int
    """
    Unix epoch timestamp of when the member joined the project.
    """
