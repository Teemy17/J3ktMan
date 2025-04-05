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


class InvitationCode(rx.Model, table=True):
    """
    An invitation code that can be used to join a project.
    """

    invitation_code: str = sql.Field(primary_key=True, nullable=False)
    """
    The alphanumeric string that represents the invitation code.
    """

    project_id: int = sql.Field(nullable=False, foreign_key="project.id")
    """
    The project ID that the invitation code is for.
    """

    created_at: int
    """
    The unix epoch timestamp of when the invitation code was created.
    """

    expired_at: int
    """
    The unix epoch timestamp of when the invitation code expires.
    """

    redeem_limit: int | None
    """
    The number of times the invitation code can be used. If None, it can be 
    used unlimited times. 
    """
