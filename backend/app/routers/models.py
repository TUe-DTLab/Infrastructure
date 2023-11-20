from typing import Optional
from uuid import UUID

import SPARQLWrapper
from fastapi import APIRouter, Header, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

import app.crud.graphdb as crud_graphdb
import app.crud.models as crud_models
import app.crud.roles as crud_roles
from app import models, schemas
from app.dependencies import GetDatabase, current_active_user
from app.util import sparql

router = APIRouter(tags=["Models"])


@router.post("/models/")
def create(
    model: schemas.ModelCreate,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    # Ensure user is verified
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Permission denied, account is not verified.")

    # Create SQL database object
    db_model = crud_models.create_model(db=db)

    # Assign role to user for model
    crud_roles.create_model_role(
        db=db, role=schemas.RoleCreateModel(role=models.RoleEnum.admin, user_id=user.id, model_id=db_model.id)
    )

    # Create graphdb repository
    crud_graphdb.create_repository(db=db, name=str(db_model.id), user=user, federation=False)

    # Initialize model data in repo
    crud_models.create_model_graph(user=user, model_id=db_model.id, model_name=model.name)
    return db_model


@router.get("/models/")
def list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(GetDatabase({models.Model: "get"})),
    user: models.User = Depends(current_active_user),
):
    return crud_models.get_models(db=db, skip=skip, limit=limit)


@router.patch("/models/{model_id}/")
def patch(
    model_id: UUID,
    model: schemas.ModelUpdate,
    db: Session = Depends(GetDatabase({models.Model: "patch"})),
    user: models.User = Depends(current_active_user),
):
    # Check if model exists
    db_model = crud_models.get_model(db=db, model_id=model_id)
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Update model
    return crud_models.update_model_graph(db=db, user=user, model_id=model_id, model=model)


@router.delete("/models/{model_id}/")
def delete(
    model_id: UUID,
    db: Session = Depends(GetDatabase({models.Model: "delete"})),
    user: models.User = Depends(current_active_user),
):
    # Delete graphdb repo
    crud_graphdb.delete_repository(db=db, name=str(model_id))

    # Delete SQL database object
    db_model = crud_models.delete_model(db=db, model_id=model_id)
    return db_model


@router.get(
    "/models/{model_id}/endpoint/",
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
    model_id: UUID,
    query: str,
    accept: Optional[str] = Header("application/sparql-results+json"),
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    model = crud_models.get_model(db=db, model_id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    if accept == "application/sparql-results+xml":
        return sparql.graphdb_query(user=user, repo_id=model_id, query=query, response_type=SPARQLWrapper.XML)
    elif accept == "application/sparql-results+json" or accept == "application/json":
        return sparql.graphdb_query(user=user, repo_id=model_id, query=query, response_type=SPARQLWrapper.JSON)
    elif accept == "application/turtle":
        return sparql.graphdb_query(user=user, repo_id=model_id, query=query, response_type=SPARQLWrapper.TURTLE)
