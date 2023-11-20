from typing import Union
from uuid import UUID

from fastapi import APIRouter, UploadFile
from fastapi.params import Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

import app.crud.file_objects as crud_file_objects
from app import models, schemas
from app.crud import models as crud_models
from app.database import StorageManager
from app.dependencies import GetDatabase, current_active_user

router = APIRouter(tags=["File objects"])


@router.get("/files/{file_id}/", response_class=FileResponse)
def read_file(
    file_id: UUID,
    db: Session = Depends(GetDatabase({models.FileObject: "get"})),
    user: models.User = Depends(current_active_user),
):
    """
    Returns the requested file object
    \f
    Args:
        file_id: the id of the file object
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database

    Returns:
        The requested file
    """
    db_file_object = crud_file_objects.get_file(db, file_id)
    file = StorageManager.get_file(db_file_object.file.path)
    return FileResponse(file.get_cdn_url(), media_type=file.content_type, filename=file.filename)


@router.post("/files/")
def create_file(
    file: UploadFile,
    name: str,
    model_id: UUID,
    db: Session = Depends(GetDatabase({models.Model: "create_file"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_file_objects.create_file(db=db, file=file, model_id=model_id, name=name)


@router.delete("/files/{file_id}/")
def delete_file(
    file_id: UUID,
    db: Session = Depends(GetDatabase({models.FileObject: "delete"})),
    user: models.User = Depends(current_active_user),
):
    """
    Deletes the specified file
    \f
    Args:
        file_id: the id of the file object
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database

    Returns:
        Nothing
    """
    crud_file_objects.delete_file(db, file_id)


@router.patch("/files/{file_id}/", response_model=schemas.FileObject)
def update_file(
    file_id: UUID,
    file_name: Union[str, None] = None,
    file: Union[UploadFile, None] = None,
    db: Session = Depends(GetDatabase({models.FileObject: "patch"})),
    user: models.User = Depends(current_active_user),
):
    """
    Update a file of the project
    \f
    Args:
        file_id: id of the file
        file_name: name of the file
        file_in: the actual updated file itself
        db: DEPENDENCY for SQLAlchemy Session object used to talk to the database

    Returns:
        The newly created file object containing the file metadata
    """

    return crud_file_objects.update_file(db=db, file_id=file_id, file_name=file_name, file=file)
