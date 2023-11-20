from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.crud.model_content as crud_model_content
import app.crud.models as crud_models
from app import models, schemas
from app.dependencies import GetDatabase, current_active_user

router = APIRouter(tags=["Models"])


@router.post("/models/{model_id}/geometry/")
def create_geometry(
    model_id: UUID,
    geometry: schemas.Geometry,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.create_geometry_graph(user=user, model_id=model_id, geometry=geometry)


@router.patch("/models/{model_id}/geometry/{geometry_id}/")
def update_geometry(
    model_id: UUID,
    geometry_id: UUID,
    geometry: schemas.GeometryUpdate,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.update_geometry_graph(
        user=user, model_id=model_id, geometry_id=geometry_id, geometry=geometry
    )


@router.delete("/models/{model_id}/geometry/{geometry_id}/")
def delete_geometry(
    model_id: UUID,
    geometry_id: UUID,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.delete_geometry_graph(user=user, model_id=model_id, geometry_id=geometry_id)


@router.post("/models/{model_id}/global_coords/")
def create_global_coords(
    model_id: UUID,
    global_coords: schemas.GlobalCoords,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.create_global_coords_graph(user=user, model_id=model_id, global_coords=global_coords)


@router.patch("/models/{model_id}/global_coords/{global_coords_id}/")
def update_global_coords(
    model_id: UUID,
    global_coords_id: UUID,
    global_coords: schemas.GlobalCoordsUpdate,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.update_global_coords_graph(
        user=user, model_id=model_id, global_coords_id=global_coords_id, global_coords=global_coords
    )


@router.delete("/models/{model_id}/global_coords/{global_coords_id}/")
def delete_global_coords(
    model_id: UUID,
    global_coords_id: UUID,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.delete_global_coords_graph(
        user=user, model_id=model_id, global_coords_id=global_coords_id
    )


@router.post("/models/{model_id}/local_coords/")
def create_local_coords(
    model_id: UUID,
    local_coords: schemas.LocalCoords,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.create_local_coords_graph(user=user, model_id=model_id, local_coords=local_coords)


@router.patch("/models/{model_id}/local_coords/{local_coords_id}/")
def update_local_coords(
    model_id: UUID,
    local_coords_id: UUID,
    local_coords: schemas.LocalCoordsUpdate,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.update_local_coords_graph(
        user=user, model_id=model_id, local_coords_id=local_coords_id, local_coords=local_coords
    )


@router.delete("/models/{model_id}/local_coords{local_coords_id}/")
def delete_local_coords(
    model_id: UUID,
    local_coords_id: UUID,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.delete_local_coords_graph(user=user, model_id=model_id, local_coords_id=local_coords_id)


@router.post("/models/{model_id}/rotation/")
def create_rotation(
    model_id: UUID,
    rotation: schemas.Rotation,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.create_rotation_graph(user=user, model_id=model_id, rotation=rotation)


@router.patch("/models/{model_id}/rotation/{rotation_id}/")
def update_rotation(
    model_id: UUID,
    rotation_id: UUID,
    rotation: schemas.RotationUpdate,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.update_rotation_graph(
        user=user, model_id=model_id, rotation_id=rotation_id, rotation=rotation
    )


@router.delete("/models/{model_id}/rotation/{rotation_id}/")
def delete_rotation(
    model_id: UUID,
    rotation_id: UUID,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.delete_rotation_graph(user=user, model_id=model_id, rotation_id=rotation_id)


@router.post("/models/{model_id}/geospatial/")
def create_geospatial(
    model_id: UUID,
    geospatial: schemas.Geospatial,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.create_geospatial_graph(user=user, model_id=model_id, geospatial=geospatial)


@router.patch("/models/{model_id}/geospatial/{geospatial_id}/")
def update_geospatial(
    model_id: UUID,
    geospatial_id: UUID,
    geospatial: schemas.GeospatialUpdate,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.update_geospatial_graph(
        user=user, model_id=model_id, geospatial_id=geospatial_id, geospatial=geospatial
    )


@router.delete("/models/{model_id}/geospatial/{geospatial_id}/")
def delete_geospatial(
    model_id: UUID,
    geospatial_id: UUID,
    db: Session = Depends(GetDatabase({models.Model: "modify_graph"})),
    user: models.User = Depends(current_active_user),
):
    crud_models.get_model(db=db, model_id=model_id)
    return crud_model_content.delete_geospatial_graph(user=user, model_id=model_id, geospatial_id=geospatial_id)
