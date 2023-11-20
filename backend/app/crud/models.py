from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.util.sparql import insert_edge, update_edge


def create_model(db: Session):
    db_model = models.Model()
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


def create_model_graph(user: models.User, model_id: UUID, model_name: str):
    insert_edge(user=user, repo_id=model_id, obj=model_id, pred="rdf:type", sub="dtlab:Model", quotes=False)
    insert_edge(user=user, repo_id=model_id, obj=model_id, pred="dtlab:modelName", sub=model_name)


def update_model_graph(db: Session, user: models.User, model_id: UUID, model: schemas.ModelUpdate):
    update_data = model.dict(exclude_unset=True)

    if "name" in update_data:
        update_edge(user=user, repo_id=model_id, obj=model_id, pred="dtlab:modelName", sub=model.name)


def delete_model(db: Session, model_id: UUID):
    db_model = db.query(models.Model).filter(models.Model.id == model_id).one_or_none()
    if db_model is None:
        raise HTTPException(status_code=404, detail="Model not found.")
    db.delete(db_model)
    db.commit()
    return db_model


def get_model(db: Session, model_id: UUID):
    return db.query(models.Model).filter(models.Model.id == model_id).first()


def get_models(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Model).offset(skip).limit(limit).all()
