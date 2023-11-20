import uuid
from uuid import UUID

from app import models, schemas
from app.util.sparql import delete_node, insert_edge, update_edge


def create_geometry_graph(user: models.User, model_id: UUID, geometry: schemas.Geometry):
    geometry_id = uuid.uuid4()

    insert_edge(user=user, repo_id=model_id, obj=geometry_id, pred="rdf:type", sub="dtlab:Geometry", quotes=False)
    insert_edge(user=user, repo_id=model_id, obj=geometry_id, pred="dtlab:geometryName", sub=geometry.name)
    insert_edge(user=user, repo_id=model_id, obj=geometry_id, pred="dtlab:geometryType", sub=str(geometry.type))
    insert_edge(
        user=user,
        repo_id=model_id,
        obj=model_id,
        pred="dtlab:hasGeometry",
        sub="dtlab:" + str(geometry_id),
        quotes=False,
    )

    if geometry.globalCoords is not None:
        insert_edge(
            user, model_id, geometry_id, "dtlab:globalCoords", "dtlab:" + str(geometry.globalCoords), quotes=False
        )

    if geometry.graphData is not None:
        insert_edge(user, model_id, geometry_id, "dtlab:graphData", "dtlab:" + str(geometry.graphData), quotes=False)

    if geometry.localCoords is not None:
        insert_edge(
            user, model_id, geometry_id, "dtlab:localCoords", "dtlab:" + str(geometry.localCoords), quotes=False
        )

    if geometry.hasRotation is not None:
        insert_edge(
            user, model_id, geometry_id, "dtlab:hasRotation", "dtlab:" + str(geometry.hasRotation), quotes=False
        )

    return geometry_id


def update_geometry_graph(user: models.User, model_id: UUID, geometry_id: UUID, geometry: schemas.GeometryUpdate):
    update_data = geometry.dict(exclude_unset=True)

    if "name" in update_data:
        update_edge(user, model_id, geometry_id, "dtlab:geometryName", geometry.name)

    if "type" in update_data:
        update_edge(user, model_id, geometry_id, "dtlab:geometryType", str(geometry.type))

    if "globalCoords" in update_data:
        update_edge(user, model_id, geometry_id, "dtlab:globalCoords", str(geometry.globalCoords), quotes=False)

    if "graphData" in update_data:
        update_edge(user, model_id, geometry_id, "dtlab:graphData", geometry.graphData, quotes=False)

    if "localCoords" in update_data:
        update_edge(user, model_id, geometry_id, "dtlab:localCoords", str(geometry.localCoords), quotes=False)

    if "hasRotation" in update_data:
        update_edge(user, model_id, geometry_id, "dtlab:hasRotation", str(geometry.hasRotation), quotes=False)


def delete_geometry_graph(user: models.User, model_id: UUID, geometry_id: UUID):
    return delete_node(user=user, repo_id=model_id, obj=geometry_id)


def create_reference_point_graph(user: models.User, model_id: UUID, reference_point: schemas.ReferencePoint):
    reference_point_id = uuid.uuid4()

    insert_edge(
        user=user, repo_id=model_id, obj=reference_point_id, pred="rdf:type", sub="dtlab:ReferencePoint", quotes=False
    )
    insert_edge(
        user=user, repo_id=model_id, obj=reference_point_id, pred="dtlab:referenceHeight", sub=reference_point.height
    )
    insert_edge(user=user, repo_id=model_id, obj=reference_point_id, pref="dtlab:referenceLat", sub=reference_point.lat)
    insert_edge(user=user, repo_id=model_id, obj=reference_point_id, pref="dtlab:referenceLon", sub=reference_point.lon)

    return reference_point_id


def update_reference_point_graph(
    user: models.User, model_id: UUID, reference_point_id: UUID, reference_point: schemas.ReferencePointUpdate
):
    update_data = reference_point.dict(exclude_unset=True)

    if "height" in update_data:
        update_edge(
            user=user,
            repo_id=model_id,
            obj=reference_point_id,
            pred="dtlab:referenceHeight",
            sub=reference_point.height,
        )

    if "lat" in update_data:
        update_edge(
            user=user, repo_id=model_id, obj=reference_point_id, pred="dtlab:referenceLat", sub=reference_point.lat
        )

    if "lon" in update_data:
        update_edge(
            user=user, repo_id=model_id, obj=reference_point_id, pred="dtlab:referenceLon", sub=reference_point.lon
        )


def delete_reference_point_graph(user: models.User, model_id: UUID, reference_point_id: UUID):
    return delete_node(user=user, repo_id=model_id, obj=reference_point_id)


def create_global_coords_graph(user: models.User, model_id: UUID, global_coords: schemas.GlobalCoords):
    global_coords_id = uuid.uuid4()

    insert_edge(
        user=user, repo_id=model_id, obj=global_coords_id, pred="rdf:type", sub="dtlab:GlobalCoordinates", quotes=False
    )

    if "x" in global_coords:
        insert_edge(user=user, repo_id=model_id, obj=global_coords_id, pred="dtlab:globalX", sub=global_coords.x)
        insert_edge(user=user, repo_id=model_id, obj=global_coords_id, pred="dtlab:globalY", sub=global_coords.y)
        insert_edge(user=user, repo_id=model_id, obj=global_coords_id, pred="dtlab:globalZ", sub=global_coords.z)
    else:
        insert_edge(
            user=user, repo_id=model_id, obj=global_coords_id, pref="dtlab:globalHeight", sub=global_coords.height
        )
        insert_edge(user=user, repo_id=model_id, obj=global_coords_id, pred="dtlab:globalLat", sub=global_coords.lat)
        insert_edge(user=user, repo_id=model_id, obj=global_coords_id, pred="dtlab:globalLon", sub=global_coords.lon)

    return global_coords_id


def update_global_coords_graph(
    user: models.User, model_id: UUID, global_coords_id: UUID, global_coords: schemas.GlobalCoordsUpdate
):
    update_data = global_coords.dict(exclude_unset=True)

    if "x" in update_data:
        update_edge(user=user, repo_id=model_id, obj=global_coords_id, pred="dtlab:globalX", sub=global_coords.x)

    if "y" in update_data:
        update_edge(user=user, repo_id=model_id, obj=global_coords_id, pred="dtlab:globalY", sub=global_coords.y)

    if "z" in update_data:
        update_edge(user=user, repo_id=model_id, obj=global_coords_id, pred="dtlab:globalZ", sub=global_coords.z)

    if "height" in update_data:
        update_edge(
            user=user, repo_id=model_id, obj=global_coords_id, pred="dtlab:globalHeight", sub=global_coords.height
        )

    if "lat" in update_data:
        update_edge(user=user, repo_id=model_id, obj=global_coords_id, pred="dtlab:globalLat", sub=global_coords.lat)

    if "lon" in update_data:
        update_edge(user=user, repo_id=model_id, obj=global_coords_id, pred="dtlab:globalLon", sub=global_coords.lon)


def delete_global_coords_graph(user: models.User, model_id: UUID, global_coords_id: UUID):
    return delete_node(user=user, repo_id=model_id, obj=global_coords_id)


def create_local_coords_graph(user: models.User, model_id: UUID, local_coords: schemas.LocalCoords):
    local_coords_id = uuid.uuid4()

    insert_edge(
        user=user, repo_id=model_id, obj=local_coords_id, pred="rdf:type", sub="dtlab:LocalCoordinates", quotes=False
    )
    insert_edge(user=user, repo_id=model_id, obj=local_coords_id, pred="dtlab:localX", sub=local_coords.x)
    insert_edge(user=user, repo_id=model_id, obj=local_coords_id, pred="dtlab:localY", sub=local_coords.y)
    insert_edge(user=user, repo_id=model_id, obj=local_coords_id, pred="dtlab:localZ", sub=local_coords.z)
    insert_edge(
        user=user,
        repo_id=model_id,
        obj=local_coords_id,
        pred="dtlab:referencePoint",
        sub=local_coords.referencePoint,
        quotes=False,
    )

    return local_coords_id


def update_local_coords_graph(
    user: models.User, model_id: UUID, local_coords_id: UUID, local_coords: schemas.LocalCoordsUpdate
):
    update_data = local_coords.dict(exclude_unset=True)

    if "x" in update_data:
        update_edge(user=user, repo_id=model_id, obj=local_coords_id, pred="dtlab:localX", sub=local_coords.x)

    if "y" in update_data:
        update_edge(user=user, repo_id=model_id, obj=local_coords_id, pred="dtlab:localY", sub=local_coords.y)

    if "z" in update_data:
        update_edge(user=user, repo_id=model_id, obj=local_coords_id, pred="dtlab:localZ", sub=local_coords.z)

    if "referencePoint" in update_data:
        update_edge(
            user=user,
            repo_id=model_id,
            obj=local_coords_id,
            pred="dtlab:referencePoint",
            sub=local_coords.referencePoint,
            quotes=False,
        )


def delete_local_coords_graph(user: models.User, model_id: UUID, local_coords_id: UUID):
    return delete_node(user=user, repo_id=model_id, obj=local_coords_id)


def create_rotation_graph(user: models.User, model_id: UUID, rotation: schemas.Rotation):
    rotation_id = uuid.uuid4()

    insert_edge(user=user, repo_id=model_id, obj=rotation_id, pred="rdf:type", sub="dtlab:Rotation", quotes=False)
    insert_edge(user=user, repo_id=model_id, obj=rotation_id, pred="dtlab:rotationX", sub=rotation.x)
    insert_edge(user=user, repo_id=model_id, obj=rotation_id, pred="dtlab:rotationY", sub=rotation.y)
    insert_edge(user=user, repo_id=model_id, obj=rotation_id, pred="dtlab:rotationZ", sub=rotation.z)

    return rotation_id


def update_rotation_graph(user: models.User, model_id: UUID, rotation_id: UUID, rotation: schemas.RotationUpdate):
    update_data = rotation.dict(exclude_unset=True)

    if "x" in update_data:
        update_edge(user=user, repo_id=model_id, obj=rotation_id, pred="dtlab:rotationX", sub=rotation.x)

    if "y" in update_data:
        update_edge(user=user, repo_id=model_id, obj=rotation_id, pred="dtlab:rotationY", sub=rotation.y)

    if "z" in update_data:
        update_edge(user=user, repo_id=model_id, obj=rotation_id, pred="dtlab:rotationZ", sub=rotation.z)


def delete_rotation_graph(user: models.User, model_id: UUID, rotation_id: UUID):
    return delete_node(user=user, repo_id=model_id, obj=rotation_id)


def create_geospatial_graph(user: models.User, model_id: UUID, geospatial: schemas.Geospatial):
    geospatial_id = uuid.uuid4()

    insert_edge(user=user, repo_id=model_id, obj=geospatial_id, pred="rdf:type", sub="dtlab:Geospatial", quotes=False)
    insert_edge(user=user, repo_id=model_id, obj=geospatial_id, pred="dtlab:geoCRS", sub=geospatial.geoCRS)
    insert_edge(user=user, repo_id=model_id, obj=geospatial_id, pred="dtlab:geoLayerName", sub=geospatial.geoLayerName)
    insert_edge(user=user, repo_id=model_id, obj=geospatial_id, pred="dtlab:geoName", sub=geospatial.geoName)
    insert_edge(user=user, repo_id=model_id, obj=geospatial_id, pred="dtlab:geoType", sub=geospatial.geoType)
    insert_edge(user=user, repo_id=model_id, obj=geospatial_id, pred="dtlab:geoURL", sub=geospatial.geoURL)

    insert_edge(
        user=user,
        repo_id=model_id,
        obj=model_id,
        pred="hasGeospatial",
        sub="dtlab:" + str(geospatial_id),
        quotes=False,
    )

    return geospatial_id


def update_geospatial_graph(
    user: models.User, model_id: UUID, geospatial_id: UUID, geospatial: schemas.GeospatialUpdate
):
    update_data = geospatial.dict(exclude_unset=True)

    if "geoCRS" in update_data:
        update_edge(user=user, repo_id=model_id, obj=geospatial_id, pred="dtlab:geoCRS", sub=geospatial.geoCRS)
    if "geoLayerName" in update_data:
        update_edge(
            user=user, repo_id=model_id, obj=geospatial_id, pred="dtlab:geoLayerName", sub=geospatial.geoLayerName
        )
    if "geoName" in update_data:
        update_edge(user=user, repo_id=model_id, obj=geospatial_id, pred="dtlab:geoName", sub=geospatial.geoName)
    if "geoType" in update_data:
        update_edge(user=user, repo_id=model_id, obj=geospatial_id, pred="dtlab:geoType", sub=geospatial.geoType)
    if "geoURL" in update_data:
        update_edge(user=user, repo_id=model_id, obj=geospatial_id, pred="dtlab:geoURL", sub=geospatial.geoURL)


def delete_geospatial_graph(user: models.User, model_id: UUID, geospatial_id: UUID):
    return delete_node(user=user, repo_id=model_id, obj=geospatial_id)
