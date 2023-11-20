from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

import app.crud.schema as crud_schema
from app import models, schemas
from app.dependencies import GetDatabase, current_active_user, current_user_admin

router = APIRouter(tags=["JSON schemas"])


@router.post("/schemas/", response_model=schemas.Schema)
def create(
    schema: schemas.SchemaCreate,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    db_schema = crud_schema.get_schema_by_name(db=db, schema_name=schema.name)
    if db_schema:
        raise HTTPException(status_code=400, detail="A schema with that name already exists.")

    return crud_schema.create_schema(db=db, schema=schema)


@router.get("/schemas/{schema_id}/", response_model=schemas.Schema)
def get(
    schema_id: UUID,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    return crud_schema.get_schema(db=db, schema_id=schema_id)


@router.get("/schemas/", response_model=List[schemas.Schema])
def list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    return crud_schema.get_schemas(db=db, skip=skip, limit=limit)


@router.delete("/schemas/{schema_id}/", response_model=schemas.Schema)
def delete(
    schema_id: UUID,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_user_admin),
):
    return crud_schema.delete_schema(db=db, schema_id=schema_id)


@router.patch("/schemas/{schema_id}/", response_model=schemas.Schema)
def patch(
    schema_id: UUID,
    schema: schemas.SchemaUpdate,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_user_admin),
):
    # TODO: handle proper updating of the schema in the database
    # requires dropping the check constraint and re-adding it to re-verify old data
    # might want to not allow updating the schema itself, only the name
    # depends on user requirements
    return crud_schema.update_schema(db=db, schema_id=schema_id, schema=schema)
