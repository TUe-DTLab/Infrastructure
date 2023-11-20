from typing import Union
from uuid import UUID

from fastapi import UploadFile
from SPARQLWrapper import BASIC, JSON, SPARQLWrapper
from sqlalchemy.orm import Session

from app import models


def graphdb_query(username: str, password: str, url: str, query: str, response_type=JSON):
    sparql = SPARQLWrapper(url + "/statements")
    sparql.setHTTPAuth(BASIC)
    sparql.setCredentials(username, password)

    sparql.setQuery(query)
    sparql.setReturnFormat(response_type)

    sparql.setMethod("POST")
    return sparql.query().convert()


def create_file(db: Session, file: UploadFile, model_id: UUID, name: str):
    db_file_object = models.FileObject(file=file, model_id=model_id, name=name)
    db.add(db_file_object)
    db.commit()
    db.refresh(db_file_object)
    return db_file_object


def get_file(db: Session, file_id: UUID):
    return db.query(models.FileObject).filter(models.FileObject.id == file_id).first()


def get_files(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.FileObject).offset(skip).limit(limit).all()


def delete_file(db: Session, file_id: UUID):
    db_file_object = db.query(models.FileObject).filter(models.FileObject.id == file_id).first()
    db.delete(db_file_object)
    db.commit()
    return db_file_object


def update_file(db: Session, file_id: UUID, file: Union[UploadFile, None], file_name: Union[str, None]):
    db_file_object = db.query(models.FileObject).filter(models.FileObject.id == file_id).first()

    if file:
        setattr(db_file_object, "file", file)
    if file_name:
        setattr(db_file_object, "name", file_name)

    db.add(db_file_object)
    db.commit()
    db.refresh(db_file_object)
    return db_file_object
