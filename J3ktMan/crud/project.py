from sqlalchemy import delete
from sqlmodel import Session
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


class InvalidProjectIDError(Exception):
    """
    Thrown when a project ID is invalid.
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
                (Project.name == info.name) & (ProjectMember.user_id == info.user_id)
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


def get_project(project_id: int) -> Project:
    with rx.session() as session:
        project = session.exec(
            Project.select().where(Project.id == project_id)
        ).first()

        if project is None:
            raise InvalidProjectIDError()

        return project


def get_projects(user_id: str) -> Sequence[Project]:
    """Returns all the projects that the user is a member of."""

    with rx.session() as session:
        return session.exec(
            Project.select().join(ProjectMember).where(ProjectMember.user_id == user_id)
        ).all()


@dataclass
class UnauthorizedError(Exception):
    """
    Thrown when a user is not authorized to perform an action.
    """

    role: Role


def is_in_project(user_id: str, project_id: int) -> bool:
    with rx.session() as session:
        project = session.exec(Project.select().where(Project.id == project_id)).first()

        if project is None:
            raise InvalidProjectIDError()

        member = session.exec(
            ProjectMember.select().where(
                (ProjectMember.project_id == project_id)
                & (ProjectMember.user_id == user_id)
            )
        ).first()

        return member is not None


def remove_expired_invitation_codes(session: Session, current_epoch: int):
    delete_expired_codes = delete(InvitationCode).where(
        (
            InvitationCode.expired_at < current_epoch  # type:ignore
        )
    )

    session.exec(delete_expired_codes)  # type: ignore
    session.commit()


def reedem_invitation_code(invitation_code: str, user_id: str) -> bool:
    """
    Redeems an invitation code for the user. Returns the Project that the
    invitation code is associated with. Returns None if the code is expired or
    invalid.
    """
    with rx.session() as session:
        current_epoch = int(datetime.datetime.now().timestamp())

        # use this opportunity to clean up expired invitation codes
        remove_expired_invitation_codes(session, current_epoch)

        invitation = session.exec(
            InvitationCode.select().where(
                (InvitationCode.invitation_code == invitation_code)
                & (InvitationCode.expired_at > current_epoch)
            )
        ).first()

        if invitation is None:
            return False

        project = session.exec(
            Project.select().where(Project.id == invitation.project_id)
        ).first()

        if project is None:
            raise InvalidProjectIDError()

        # check if the user is already a member of the project
        existing_member = session.exec(
            ProjectMember.select().where(
                (ProjectMember.project_id == project.id)
                & (ProjectMember.user_id == user_id)
            )
        ).first()

        if existing_member is not None:
            return True

        # check if the invitation code has a redeem limit
        delete_code = False
        if invitation.redeem_limit is not None:
            invitation.redeem_limit -= 1
            delete_code = invitation.redeem_limit == 0

        # add the user as a member of the project
        new_member = ProjectMember(
            project_id=project.id,
            user_id=user_id,
            role=Role.COLLABORATOR,
            joined_at=current_epoch,
        )

        session.add(new_member)

        if delete_code:
            session.delete(invitation)

        session.commit()

        return True


def get_project_from_invitation_code(
    invitation_code: str,
) -> Project | None:
    """
    Gets the Project that the invitation code is associated with. Returns None
    if the code is expired or invalid.
    """
    with rx.session() as session:
        current_epoch = int(datetime.datetime.now().timestamp())

        invitation = session.exec(
            InvitationCode.select().where(
                (InvitationCode.invitation_code == invitation_code)
                & (InvitationCode.expired_at > current_epoch)
            )
        ).first()

        if invitation is None:
            return None

        project = session.exec(
            Project.select().where(Project.id == invitation.project_id)
        ).first()

        if project is None:
            raise ValueError("Project not found")

        return project


def get_invitation_code(
    user_id: str, project: int, duration: int, redeem_limit: int | None
) -> str:
    assert duration > 0
    assert redeem_limit is None or redeem_limit > 0

    with rx.session() as session:
        current_epoch = int(datetime.datetime.now().timestamp())

        # use this opportunity to clean up expired invitation codes
        remove_expired_invitation_codes(session, current_epoch)

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
                InvitationCode.select().where(InvitationCode.invitation_code == code)
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
