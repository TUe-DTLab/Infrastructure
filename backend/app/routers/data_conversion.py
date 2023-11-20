from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.crud.file_objects as crud_file_objects
import app.crud.models as crud_models
from app import models
from app.data_converters import conversion
from app.dependencies import GetDatabase, current_active_user

router = APIRouter(tags=["Data conversion"])


@router.post("/data_conversion/ifc2gltf/")
def convert_ifc2gltf(
    file_id: UUID,
    db: Session = Depends(GetDatabase({models.Model: "create_file", models.FileObject: "get"})),
    user: models.User = Depends(current_active_user),
):
    # Validates permissions
    db_file_object = crud_file_objects.get_file(db=db, file_id=file_id)
    crud_models.get_model(db=db, model_id=db_file_object.model_id)

    return conversion.convert_ifc_to_gltf(db=db, file_id=file_id)


@router.post("/data_conversion/ifc2components/")
def convert_ifc2components():
    pass


@router.post("/data_conversion/ifc2ttl/")
def convert_ifc2ttl(
    file_id: UUID, db: Session = Depends(GetDatabase(None)), user: models.User = Depends(current_active_user)
):
    # Validates permissions
    db_file_object = crud_file_objects.get_file(db=db, file_id=file_id)
    crud_models.get_model(db=db, model_id=db_file_object.model_id)

    return conversion.convert_ifc_to_ttl(db=db, file_id=file_id)
