from typing import List
from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

import app.crud.roles as crud_roles
from app import models, schemas
from app.crud import models as crud_models
from app.crud import projects as crud_projects
from app.dependencies import GetDatabase, current_active_user

router_project = APIRouter(tags=["Projects"])
router_model = APIRouter(tags=["Models"])


@router_project.get("/projects/roles/", response_model=List[schemas.RoleProject])
def list_project_roles(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(GetDatabase({models.RoleProject: "get"})),
    user: models.User = Depends(current_active_user),
):
    """
    Lists all roles related to the specified project
    \f
    Args:
        project_id: the project of which to get the related roles
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database
        user: DEPENDENCY for currently logged in object used for authentication

    Returns:
        A serialized list of roles
    """
    return crud_roles.list_project_roles(db=db, project_id=project_id, skip=skip, limit=limit)


@router_project.post("/projects/roles/", response_model=schemas.RoleProject)
def create_project_role(
    role: schemas.RoleCreateProject,
    db: Session = Depends(GetDatabase({models.Project: "create_roles"})),
    user: models.User = Depends(current_active_user),
):
    """
    Creates a role for the specified project
    \f
    Args:
        role: Role schema containing the email, role name and project id for the role to be created
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database
        user: DEPENDENCY for currently logged in object used for authentication

    Returns:
        A serialized copy of the newly created role
    """
    crud_projects.get_project(db=db, project_id=role.project_id)
    if role.role == models.RoleEnum.guest:
        crud_roles.grant_graphdb_permissions(user, role.project_id, read=True, write=False)
        crud_roles.grant_graphdb_permissions(user, str(role.project_id) + "-subrepo", read=True, write=False)
    elif role.role == models.RoleEnum.maintainer or models.RoleEnum.admin:
        crud_roles.grant_graphdb_permissions(user, role.project_id, read=True, write=True)
        crud_roles.grant_graphdb_permissions(user, str(role.project_id) + "-subrepo", read=True, write=True)
    return crud_roles.create_project_role(db=db, role=role)


@router_project.delete("/projects/roles/")
def delete_project_role(
    role: schemas.RoleDeleteProject,
    db: Session = Depends(GetDatabase({models.RoleProject: "delete"})),
    user: models.User = Depends(current_active_user),
):
    """
    Deletes the specified role from the project
    \f
    Args:
        role: RoleDelete schema containing the email and project id of the role to be deleted
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database
        user: DEPENDENCY for currently logged in object used for authentication

    Returns:
        null
    """
    response = crud_roles.delete_project_role(db=db, role=role)

    crud_roles.revoke_graphdb_permissions(user, role.project_id, read=True, write=True)
    crud_roles.revoke_graphdb_permissions(user, str(role.project_id) + "-subrepo", read=True, write=True)

    return response


@router_project.patch("/projects/roles/")
def patch_project_role(
    role: schemas.RoleUpdateProject,
    db: Session = Depends(GetDatabase({models.RoleProject: "patch"})),
    user: models.User = Depends(current_active_user),
):
    """
    Update the specified role from the project
    \f
    Args:
        role: RoleUpdate schema containing the email and project id of the role to be deleted
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database
        user: DEPENDENCY for currently logged in object used for authentication

    Returns:
        null
    """
    response = crud_roles.update_project_role(db=db, role=role)

    crud_roles.revoke_graphdb_permissions(user, role.project_id, read=True, write=True)
    crud_roles.revoke_graphdb_permissions(user, str(role.project_id) + "-subrepo", read=True, write=True)

    if role.role == models.RoleEnum.guest:
        crud_roles.grant_graphdb_permissions(user, role.project_id, read=True, write=False)
        crud_roles.grant_graphdb_permissions(user, str(role.project_id) + "-subrepo", read=True, write=False)
    elif role.role == models.RoleEnum.maintainer or models.RoleEnum.admin:
        crud_roles.grant_graphdb_permissions(user, role.project_id, read=True, write=True)
        crud_roles.grant_graphdb_permissions(user, str(role.project_id) + "-subrepo", read=True, write=True)

    return response


@router_model.get("/models/roles/", response_model=List[schemas.RoleModel])
def list_model_roles(
    model_id: UUID,
    db: Session = Depends(GetDatabase({models.RoleModel: "get"})),
    user: models.User = Depends(current_active_user),
):
    """
    Lists all roles related to the specified project
    \f
    Args:
        project_id: the project of which to get the related roles
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database
        user: DEPENDENCY for currently logged in object used for authentication

    Returns:
        A serialized list of roles
    """
    return crud_roles.list_model_roles(db=db, model_id=model_id)


@router_model.post("/models/roles/", response_model=schemas.RoleModel)
def create_model_role(
    role: schemas.RoleCreateModel,
    db: Session = Depends(GetDatabase({models.Model: "create_roles"})),
    user: models.User = Depends(current_active_user),
):
    """
    Creates a role for the specified project
    \f
    Args:
        role: Role schema containing the email, role name and project id for the role to be created
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database
        user: DEPENDENCY for currently logged in object used for authentication

    Returns:
        A serialized copy of the newly created role
    """
    crud_models.get_model(db=db, model_id=role.model_id)
    if role.role == models.RoleEnum.guest:
        crud_roles.grant_graphdb_permissions(user, role.model_id, read=True, write=False)
    elif role.role == models.RoleEnum.maintainer or models.RoleEnum.admin:
        crud_roles.grant_graphdb_permissions(user, role.model_id, read=True, write=True)
    return crud_roles.create_model_role(db=db, role=role)


@router_model.delete("/models/roles/", response_model=schemas.RoleModel)
def delete_model_role(
    role: schemas.RoleDeleteModel,
    db: Session = Depends(GetDatabase({models.RoleModel: "delete"})),
    user: models.User = Depends(current_active_user),
):
    """
    Deletes the specified role from the project
    \f
    Args:
        role: RoleDelete schema containing the email and project id of the role to be deleted
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database
        user: DEPENDENCY for currently logged in object used for authentication

    Returns:
        null
    """
    response = crud_roles.delete_model_role(db=db, role=role)

    crud_roles.revoke_graphdb_permissions(user, role.model_id, read=True, write=True)

    return response


@router_model.patch("/models/roles/")
def patch_model_role(
    role: schemas.RoleUpdateModel,
    db: Session = Depends(GetDatabase({models.RoleModel: "patch"})),
    user: models.User = Depends(current_active_user),
):
    """
    Update the specified role from the project
    \f
    Args:
        role: RoleUpdate schema containing the email and project id of the role to be deleted
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database
        user: DEPENDENCY for currently logged in object used for authentication

    Returns:
        null
    """
    response = crud_roles.update_model_role(db=db, role=role)

    crud_roles.revoke_graphdb_permissions(user, role.model_id, read=True, write=True)

    if role.role == models.RoleEnum.guest:
        crud_roles.grant_graphdb_permissions(user, role.model_id, read=True, write=False)
    elif role.role == models.RoleEnum.maintainer or models.RoleEnum.admin:
        crud_roles.grant_graphdb_permissions(user, role.model_id, read=True, write=True)

    return response
