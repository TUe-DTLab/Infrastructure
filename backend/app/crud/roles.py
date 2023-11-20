import base64
from uuid import UUID

import requests
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import config


def grant_graphdb_permissions(user: models.User, repository_id: str, read=True, write=False):
    credentials = "%s:%s" % (config["GRAPHDB_USER"], config["GRAPHDB_PASSWD"])
    headers = {"Authorization": "Basic %s" % base64.b64encode(credentials.encode("utf-8")).decode("utf-8")}

    # get current user info
    graph_user = requests.get(
        f"{config['GRAPHDB_URL']}/rest/security/users/{user.graphdb_username}", headers=headers
    ).json()

    # update user info
    if read:
        graph_user["grantedAuthorities"].append("READ_REPO_" + repository_id)
    if write:
        graph_user["grantedAuthorities"].append("WRITE_REPO_" + repository_id)
    del graph_user["password"]

    # write new user info
    requests.put(
        f"{config['GRAPHDB_URL']}/rest/security/users/{user.graphdb_username}", json=graph_user, headers=headers
    )


def revoke_graphdb_permissions(user: models.User, repository_id: str, read=True, write=True):
    credentials = "%s:%s" % (config["GRAPHDB_USER"], config["GRAPHDB_PASSWD"])
    headers = {"Authorization": "Basic %s" % base64.b64encode(credentials.encode("utf-8")).decode("utf-8")}

    # get current user info
    graph_user = requests.get(
        f"{config['GRAPHDB_URL']}/rest/security/users/{user.graphdb_username}", headers=headers
    ).json()

    # update user info
    if read:
        graph_user["grantedAuthorities"].remove("READ_REPO_" + repository_id)
    if read or write:
        graph_user["grantedAuthorities"].remove("WRITE_REPO_" + repository_id)
    del graph_user["password"]

    # write new user info
    requests.put(
        f"{config['GRAPHDB_URL']}/rest/security/users/{user.graphdb_username}", json=graph_user, headers=headers
    )


def create_project_role(db: Session, role: schemas.RoleCreateProject):
    db_role = models.RoleProject(**role.dict())

    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def list_project_roles(db: Session, project_id: UUID, skip: int = 0, limit: int = 100):
    return (
        db.query(models.RoleProject).filter(models.RoleProject.project_id == project_id).offset(skip).limit(limit).all()
    )


def update_project_role(db: Session, role: schemas.RoleUpdateProject):
    db_role = (
        db.query(models.RoleProject)
        .filter(models.RoleProject.project_id == role.project_id, models.RoleProject.user_id == role.user_id)
        .first()
    )
    setattr(db_role, "role", role.role)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def delete_project_role(db: Session, role: schemas.RoleDeleteProject):
    db_role = (
        db.query(models.RoleProject)
        .filter(models.RoleProject.project_id == role.project_id, models.RoleProject.user_id == role.user_id)
        .first()
    )
    db.delete(db_role)
    db.commit()
    return db_role


def create_model_role(db: Session, role: schemas.RoleCreateModel):
    db_role = models.RoleModel(**role.dict())

    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def list_model_roles(db: Session, model_id: UUID, skip: int = 0, limit: int = 100):
    return db.query(models.RoleModel).filter(models.RoleModel.model_id == model_id).offset(skip).limit(limit).all()


def update_model_role(db: Session, role: schemas.RoleUpdateModel):
    db_role = (
        db.query(models.RoleModel)
        .filter(models.RoleModel.model_id == role.model_id, models.RoleModel.user_id == role.user_id)
        .first()
    )
    setattr(db_role, "role", role.role)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def delete_model_role(db: Session, role: schemas.RoleDeleteModel):
    db_role = (
        db.query(models.RoleModel)
        .filter(models.RoleModel.model_id == role.model_id, models.RoleModel.user_id == role.user_id)
        .first()
    )
    db.delete(db_role)
    db.commit()
    return db_role
