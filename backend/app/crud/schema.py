from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import not_found


def create_schema(db: Session, schema: schemas.SchemaCreate):
    db_schema = models.Schema(**schema.dict())
    db.add(db_schema)
    db.commit()
    db.refresh(db_schema)
    return db_schema


def delete_schema(db: Session, schema_id: UUID):
    db_schema = db.query(models.Schema).filter(models.Schema.id == schema_id).first()
    db.delete(db_schema)
    db.commit()
    return db_schema


def get_schema(db: Session, schema_id: UUID):
    db_schema = db.query(models.Schema).filter(models.Schema.id == schema_id).first()
    return db_schema


def get_schema_by_name(db: Session, schema_name: str):
    db_schema = db.query(models.Schema).filter(models.Schema.name == schema_name).first()
    return db_schema


def get_schemas(db: Session, skip: int = 0, limit: int = 100):
    db_schemas = db.query(models.Schema).offset(skip).limit(limit).all()
    return db_schemas


def update_schema(db: Session, schema_id: UUID, schema: schemas.SchemaUpdate):
    db_schema = db.query(models.Schema).filter(models.Schema.id == schema_id).first()
    if not db_schema:
        not_found()

    update_data = schema.dict(exclude_unset=True)
    for field in jsonable_encoder(db_schema):
        if field in update_data:
            setattr(db_schema, field, update_data[field])

    db.add(db_schema)
    db.commit()
    db.refresh(db_schema)
    return db_schema
