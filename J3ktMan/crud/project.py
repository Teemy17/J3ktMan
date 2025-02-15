from typing import Sequence
from J3ktMan.model.project import Project, ProjectMember, Role
import reflex as rx
import datetime


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
