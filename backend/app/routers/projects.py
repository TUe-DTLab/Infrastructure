from typing import List, Optional, Union
from uuid import UUID

import SPARQLWrapper
from fastapi import APIRouter, Header, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

import app.crud.graphdb as crud_graphdb
import app.crud.projects as crud_projects
import app.crud.roles as crud_roles
from app import models, schemas
from app.dependencies import GetDatabase, current_active_user
from app.util import sparql

router = APIRouter(tags=["Projects"])


@router.post(
    "/projects/",
    response_model=schemas.Project,
)
def create(
    project: schemas.ProjectCreate,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    """
    Creates a new project object
    \f
    Args:
        project: ProjectCreate schema with all the information needed to create a project
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database

    Returns:
        A serialized copy of the newly created project
    """
    # Ensure user is verified
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Permission denied, account is not verified.")

    # Create SQL database object
    db_project = crud_projects.create_project(db=db, project=project)

    # Assign role to user for project
    crud_roles.create_project_role(
        db=db, role=schemas.RoleCreateProject(role=models.RoleEnum.admin, user_id=user.id, project_id=db_project.id)
    )

    # Create graphdb repository
    crud_graphdb.create_repository(db=db, name=str(db_project.id), user=user, federation=True)

    # Initialize project data in repo
    crud_projects.create_project_graph(user=user, project_id=db_project.id, project_name=project.name + "-subrepo")

    return db_project


@router.get("/projects/", response_model=List[schemas.Project])
def list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(GetDatabase({models.Project: "get"})),
    user: models.User = Depends(current_active_user),
):
    """
    Lists all projects
    \f
    Args:
        skip: the number of projects the results will be offset by
        limit: the number of projects that will be returned
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database

    Returns:
        A serialized list of projects
    """
    return crud_projects.get_projects(db=db, skip=skip, limit=limit)


@router.delete("/projects/{project_id}/", response_model=schemas.RoleProject)
def delete(
    project_id: UUID,
    db: Session = Depends(GetDatabase({models.Project: "delete"})),
    user: models.User = Depends(current_active_user),
):
    """
    Deletes the specified project
    \f
    Args:
        project_id: The id of the project to delete
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database

    Returns:
        Nothing
    """
    db_project = crud_projects.delete_project(db=db, project_id=project_id)

    crud_graphdb.delete_repository(db=db, name=str(project_id))
    crud_graphdb.delete_repository(db=db, name=str(project_id) + "-subrepo")

    return db_project


@router.patch("/projects/{project_id}/")
def patch(
    project_id: UUID,
    project: schemas.ProjectUpdate,
    db: Session = Depends(GetDatabase({models.Project: "patch"})),
    user: models.User = Depends(current_active_user),
):
    """
    Updates the specified project
    \f
    Args:
        project_id: The id of the project to delete
        project_in: A ProjectUpdate schema with any of the data needed to update the project
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database

    Returns:
        A serialized copy of the updated project data
    """
    db_project = crud_projects.get_project(db=db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    return crud_projects.update_project_graph(db=db, user=user, project_id=project_id, project=project)


@router.get("/projects/{project_id}/federation/")
def get_federation_members(
    project_id: UUID,
    db: Session = Depends(GetDatabase({models.Project: "get"})),
    user: models.User = Depends(current_active_user),
):
    project = crud_projects.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return crud_graphdb.get_federation_members(db=db, user=user, project_id=project_id)


@router.post("/projects/{project_id}/federation/")
def add_federation_member(
    project_id: UUID,
    member: Union[schemas.ResolvableRepository, schemas.SPARQLEndpointWrite],
    db: Session = Depends(GetDatabase({models.Project: "patch"})),
    user: models.User = Depends(current_active_user),
):
    # TODO: check proper permissions of target repo
    project = crud_projects.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    crud_graphdb.add_federation_member(db=db, user=user, project_id=project_id, member=member)
    crud_graphdb.restart_repository(db=db, user=user, project_id=project_id)
    return


@router.delete("/project/{project_id}/federation/")
def delete_federation_member(
    project_id: UUID,
    member: Union[schemas.ResolvableRepository, schemas.SPARQLEndpointWrite],
    db: Session = Depends(GetDatabase({models.Project: "patch"})),
    user: models.User = Depends(current_active_user),
):
    project = crud_projects.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    crud_graphdb.remove_federation_member(db=db, user=user, project_id=project_id, member=member)
    crud_graphdb.restart_repository(db=db, user=user, project_id=project_id)


@router.post("/projects/{project_id}/models/")
def add_model(
    project_id: UUID,
    model_id: UUID,
    db: Session = Depends(GetDatabase({models.Project: "patch"})),
    user: models.User = Depends(current_active_user),
):
    return crud_projects.add_model(user=user, project_id=project_id, model_id=model_id)


@router.delete("/projects/{project_id}/models/")
def remove_model(
    project_id: UUID,
    model_id: UUID,
    db: Session = Depends(GetDatabase({models.Project: "patch"})),
    user: models.User = Depends(current_active_user),
):
    return crud_projects.remove_model(user=user, project_id=project_id, model_id=model_id)


@router.get(
    "/projects/{project_id}/endpoint/",
    response_model=None,
    responses={
        200: {
            "content": {
                "application/sparql-results+xml": {},
                "application/sparql-results+json": {},
                "application/turtle": {},
            },
            "description": "Return the sparql results",
        }
    },
)
def sparql_endpoint(
    project_id: UUID,
    query: str,
    accept: Optional[str] = Header("application/sparql-results+json"),
    db: Session = Depends(GetDatabase({models.Project: "get"})),
    user: models.User = Depends(current_active_user),
):
    project = crud_projects.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Model not found")

    if accept == "application/sparql-results+xml":
        return sparql.graphdb_query(user=user, repo_id=project_id, query=query, response_type=SPARQLWrapper.XML)
    elif accept == "application/sparql-results+json" or accept == "application/json":
        return sparql.graphdb_query(user=user, repo_id=project_id, query=query, response_type=SPARQLWrapper.JSON)
    elif accept == "application/turtle":
        return sparql.graphdb_query(user=user, repo_id=project_id, query=query, response_type=SPARQLWrapper.TURTLE)
