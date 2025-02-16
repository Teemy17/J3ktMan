from sqlalchemy import delete
from J3ktMan.model.project import InvitationCode, Project, ProjectMember, Role

from dataclasses import dataclass
from typing import Sequence

import reflex as rx

import datetime
import random
import string


class ProjectCreate(rx.Base):
    user_id: str
    name: str


class ExistingProjectNameError(Exception):
    """
    Thrown when a project with the same name with the same user already exists.
    """

    pass


class TooShortProjectNameError(Exception):
    """
    Thrown when a project name is less than 4 characters.
    """

    pass


def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def create_project(info: ProjectCreate) -> Project:
    if len(info.name) < 4:
        raise TooShortProjectNameError()

    with rx.session() as session:
        current_time = int(datetime.datetime.now().timestamp())

        # check if there's a project with the same name for this user
        existing_project = session.exec(
            Project.select()
            .join(ProjectMember)
            .where(
                (Project.name == info.name)
                & (ProjectMember.user_id == info.user_id)
            )
        ).first()

        if existing_project is not None:
            raise ExistingProjectNameError()

        project = Project(
            name=info.name,
            created_at=current_time,
            starting_date=current_time,
        )

        session.add(project)
        session.commit()
        session.refresh(project)

        project_member = ProjectMember(
            project_id=project.id,
            joined_at=current_time,
            role=Role.OWNER,
            user_id=info.user_id,
        )

        session.add(project_member)
        session.commit()

        return project


def get_projects(user_id: str) -> Sequence[Project]:
    """Returns all the projects that the user is a member of."""

    with rx.session() as session:
        return session.exec(
            Project.select()
            .join(ProjectMember)
            .where(ProjectMember.user_id == user_id)
        ).all()


@dataclass
class UnauthorizedError(Exception):
    """
    Thrown when a user is not authorized to perform an action.
    """

    role: Role


def get_invitation_code(
    user_id: str, project: int, duration: int, redeem_limit: int | None
) -> str:
    assert duration > 0
    assert redeem_limit is None or redeem_limit > 0

    with rx.session() as session:
        current_epoch = int(datetime.datetime.now().timestamp())

        # use this opportunity to clean up expired invitation codes
        delete_expired_codes = delete(InvitationCode).where(
            (InvitationCode.expired_at < current_epoch)  # type: ignore
        )

        session.exec(delete_expired_codes)  # type: ignore
        session.commit()

        # make sure the user is the owner of the project
        project_member = session.exec(
            ProjectMember.select().where(
                (ProjectMember.user_id == user_id)
                & (ProjectMember.project_id == project)
                & (ProjectMember.role == Role.OWNER)
            )
        ).first()

        if project_member is None:
            raise UnauthorizedError(role=Role.OWNER)

        # check if there's an existing invitation code that hasn't expired
        existing_code = session.exec(
            InvitationCode.select().where(
                (InvitationCode.project_id == project)
                & (InvitationCode.expired_at > current_epoch)
            )
        ).first()

        if existing_code is not None:
            return existing_code.invitation_code

        # create a new invitation code
        code = generate_random_string()

        # pedantic: in case of very unluckly dude who gets the same code
        while True:
            existing_code = session.exec(
                InvitationCode.select().where(
                    InvitationCode.invitation_code == code
                )
            ).first()

            if existing_code is None:
                break

            code = generate_random_string()

        new_invitation_code = InvitationCode(
            project_id=project,
            invitation_code=code,
            expired_at=current_epoch + duration,
            redeem_limit=redeem_limit,
            created_at=current_epoch,
        )

        session.add(new_invitation_code)
        session.commit()

        return code
