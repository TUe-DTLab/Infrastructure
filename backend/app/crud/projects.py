from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.util.sparql import delete_edge, insert_edge, update_edge


def create_project(db: Session, project: schemas.ProjectCreate):
    """
    Creates a project in the database

    Args:
        db: SQLAlchemy Session object used to talk to the database
        project: ProjectCreate schema with all the  information needed to create a project

    Returns:
        The created project database object
    """
    db_project = models.Project(public=project.public)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def create_project_graph(user: models.User, project_id: UUID, project_name: str):
    insert_edge(user=user, repo_id=str(project_id) + "-subrepo", obj=project_id, pred="rdf:type", sub=project_name)
    insert_edge(
        user=user, repo_id=str(project_id) + "-subrepo", obj=project_id, pred="dtlab:projectName", sub=project_name
    )


def update_project_graph(db: Session, user: models.User, project_id: UUID, project: schemas.ProjectUpdate):
    update_data = project.dict(exclude_unset=True)

    if "name" in update_data:
        update_edge(
            user=user, repo_id=str(project_id) + "-subrepo", obj=project_id, pred="dtlab:projectName", sub=project.name
        )


def delete_project(db: Session, project_id: UUID):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).one_or_none()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    db.delete(db_project)
    db.commit()
    return db_project


def get_project(db: Session, project_id: UUID):
    """
    Retrieves a project from the database by id

    Args:
        db: SQLAlchemy Session object used to talk to the database
        project_id: id of the project to be retrieved

    Returns:
        The requested project database object or None if not found
    """
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def get_projects(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves all project from the database

    Args:
        db: SQLAlchemy Session object used to talk to the database
        skip: the number of projects the results will be offset by
        limit: the number of projects that will be returned

    Returns:
        The projects in the database as limited and offset by the given parameters
    """
    return db.query(models.Project).offset(skip).limit(limit).all()


def add_model(user: models.User, project_id: UUID, model_id: UUID):
    # add edge connecting project and model
    insert_edge(
        user=user,
        repo_id=str(project_id) + "-subrepo",
        obj=project_id,
        pred="dtlab:hasModel",
        sub=f"dtlab:{model_id}",
        quotes=False,
    )


def remove_model(user: models.User, project_id: UUID, model_id: UUID):
    # delete edge connecting project and model
    delete_edge(
        user=user,
        repo_id=str(project_id) + "-subrepo",
        obj=project_id,
        pred="dtlab:hasModel",
        sub=f"dtlab:{model_id}",
        quotes=False,
    )
