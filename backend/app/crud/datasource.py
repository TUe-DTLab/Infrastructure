from typing import List
from uuid import UUID

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from psycopg2.errors import CheckViolation, UniqueViolation
from sqlalchemy import asc, desc, func, select
from sqlalchemy.dialects.postgresql import INTERVAL, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, with_polymorphic

from app import models, schemas
from app.database import not_found
from app.schemas.datasource import AggregateFunctionEnum
from app.util.sparql import delete_edge, delete_node, insert_edge, update_edge


def create_datasource(db: Session, datasource: schemas.DataSourceCreateUnion):
    db_model = db.query(models.Model).filter(models.Model.id == datasource.model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Project not found.")
    match datasource.type:
        case "float":
            db_datasource = models.DataSourceFloat(**datasource.dict())
        case "vector3":
            db_datasource = models.DataSourceVector3(**datasource.dict())
        case "json":
            db_datasource = models.DataSourceJSON(**datasource.dict())
    db.add(db_datasource)
    db.commit()
    db.refresh(db_datasource)
    return db_datasource


def create_datasource_graph(user: models.User, datasource_id: UUID, datasource: schemas.DataSourceCreateUnion):
    insert_edge(
        user=user, repo_id=datasource.model_id, obj=datasource_id, pred="rdf:type", sub="dtlab:Datasource", quotes=False
    )
    insert_edge(
        user=user, repo_id=datasource.model_id, obj=datasource_id, pred="dtlab:datasourceName", sub=datasource.name
    )
    insert_edge(
        user=user, repo_id=datasource.model_id, obj=datasource_id, pred="dtlab:datasourceType", sub=datasource.type
    )

    insert_edge(
        user=user,
        repo_id=datasource.model_id,
        obj=datasource.model_id,
        pred="dtlab:hasDatasource",
        sub="dtlab:" + str(datasource_id),
        quotes=False,
    )

    if datasource.type == models.DataSourceEnum.json:
        insert_edge(
            user=user, repo_id=datasource.model_id, obj=datasource_id, pred="dtlab:hasSchema", sub=datasource.schema_id
        )


def delete_datasource(db: Session, datasource_id: UUID):
    db_datasource = db.query(models.DataSource).filter(models.DataSource.id == datasource_id).first()
    db.delete(db_datasource)
    db.commit()
    return db_datasource


def delete_datasource_graph(user: models.User, model_id: UUID, datasource_id: UUID):
    delete_node(user=user, repo_id=model_id, obj=datasource_id)


def get_datasource(db: Session, datasource_id: UUID):
    db_datasource = (
        db.query(
            with_polymorphic(
                models.DataSource, [models.DataSourceFloat, models.DataSourceVector3, models.DataSourceJSON]
            )
        )
        .filter(models.DataSource.id == datasource_id)
        .first()
    )
    return db_datasource


def get_datasource_by_name(db: Session, model_id: UUID, name: str):
    db_datasource = (
        db.query(
            with_polymorphic(
                models.DataSource, [models.DataSourceFloat, models.DataSourceVector3, models.DataSourceJSON]
            )
        )
        .filter(models.DataSource.model_id == model_id, models.DataSource.name == name)
        .one_or_none()
    )
    return db_datasource


def update_datasource(db: Session, datasource_id: UUID, datasource: schemas.DataSourceUpdateUnion):
    db_datasource = (
        db.query(
            with_polymorphic(
                models.DataSource, [models.DataSourceFloat, models.DataSourceVector3, models.DataSourceJSON]
            )
        )
        .filter(models.DataSource.id == datasource_id)
        .first()
    )
    if not db_datasource:
        not_found()

    update_data = datasource.dict(exclude_unset=True)
    for field in jsonable_encoder(db_datasource):
        if field in update_data:
            setattr(db_datasource, field, update_data[field])
    db.add(db_datasource)
    db.commit()
    db.refresh(db_datasource)
    return db_datasource


def update_datasource_graph(
    user: models.User, model_id: UUID, datasource_id: UUID, datasource: schemas.DataSourceUpdateUnion
):
    update_data = datasource.dict(exclude_unset=True)
    if "name" in update_data:
        update_edge(user=user, repo_id=model_id, obj=datasource_id, pred="dtlab:datasourceName", sub=datasource.name)
    if "schema_id" in update_data:
        update_edge(user=user, repo_id=model_id, obj=datasource_id, pred="dtlab:hasSchema", sub=datasource.schema_id)


def query_datasource(db: Session, datasource_id: UUID, query: schemas.Query):
    db_datasource = db.query(models.DataSource).filter(models.DataSource.id == datasource_id).first()
    if not db_datasource:
        raise HTTPException(status_code=404, detail="Datasource not found.")

    if query.aggregate_function:
        match query.aggregate_function:
            case AggregateFunctionEnum.MEAN:
                aggr_fun = func.avg
            case AggregateFunctionEnum.STD:
                aggr_fun = func.std
            case AggregateFunctionEnum.SUM:
                aggr_fun = func.sum
            case AggregateFunctionEnum.MIN:
                aggr_fun = func.min
            case AggregateFunctionEnum.MAX:
                aggr_fun = func.max
            case AggregateFunctionEnum.COUNT:
                aggr_fun = func.count

    match db_datasource.type:
        case models.DataSourceEnum.float:
            if query.aggregate_bucket and query.aggregate_function:
                stmt = select(
                    func.time_bucket(func.cast(query.aggregate_bucket, INTERVAL), models.DataPointFloat.datetime).label(
                        "datetime_bucket"
                    ),
                    aggr_fun(models.DataPointFloat.value).label("value"),
                )
                stmt = stmt.group_by("datetime_bucket")
                stmt = (
                    stmt.order_by(asc("datetime_bucket"))
                    if query.time_ascending
                    else stmt.order_by(desc("datetime_bucket"))
                )
            else:
                stmt = select(models.DataPointFloat.datetime, models.DataPointFloat.value)
                stmt = (
                    stmt.order_by(models.DataPointFloat.datetime.asc())
                    if query.time_ascending
                    else stmt.order_by(models.DataPointFloat.datetime.desc())
                )

            stmt = stmt.where(models.DataPointFloat.datasource_id == datasource_id)

            if query.start_date:
                stmt = stmt.where(models.DataPointFloat.datetime > query.start_date)
            if query.end_date:
                stmt = stmt.where(models.DataPointFloat.datetime < query.end_date)

            stmt = stmt.offset(query.skip).limit(query.limit)
        case models.DataSourceEnum.vector3:
            if query.aggregate_bucket or query.aggregate_function:
                raise HTTPException(400, "Aggregation not supported for vector3 datasource type")

            stmt = select(models.DataPointVector3).where(models.DataPointVector3.datasource_id == datasource_id)

            if query.start_date:
                stmt = stmt.where(models.DataPointVector3.datetime > query.start_date)
            if query.end_date:
                stmt = stmt.where(models.DataPointVector3.datetime < query.end_date)

            stmt = stmt.order_by(
                models.DataPointVector3.datetime.asc()
                if query.time_ascending
                else stmt.order_by(models.DataPointVector3.datetime.desc())
            )

            stmt = stmt.offset(query.skip).limit(query.limit)
        case models.DataSourceEnum.json:
            if query.aggregate_bucket or query.aggregate_function:
                raise HTTPException(400, "Aggregation not supported for json datasource type")
            stmt = select(models.DataPointJSON).where(models.DataPointJSON.datasource_id == datasource_id)

            if query.start_date:
                stmt = stmt.where(models.DataPointJSON.datetime > query.start_date)
            if query.end_date:
                stmt = stmt.where(models.DataPointJSON.datetime < query.end_date)

            stmt = stmt.order_by(
                models.DataPointJSON.datetime.asc()
                if query.time_ascending
                else stmt.order_by(models.DataPointJSON.datetime.desc())
            )

            stmt = stmt.offset(query.skip).limit(query.limit)

    return db.execute(stmt).all()


def query_bulk_datasource(db: Session, query: schemas.QueryBulk):
    data = []
    for datasource_id in query.datasource_ids:
        data.append(
            {
                "datasource_id": datasource_id,
                "results": query_datasource(db=db, datasource_id=datasource_id, query=query.query),
            }
        )
    return data


def get_datasource_stats(db: Session, datasource_id: UUID):
    db_datasource = db.query(models.DataSource).filter(models.DataSource.id == datasource_id).first()
    if not db_datasource:
        raise HTTPException(status_code=404, detail="Datasource not found.")

    match db_datasource.type:
        case "float":
            result = {}

            # common
            result["count"] = db.execute(
                select(func.count(models.DataPointFloat.datetime)).where(
                    models.DataPointFloat.datasource_id == datasource_id
                )
            ).scalar()
            result["count_distinct"] = db.execute(
                select(func.count(func.distinct(models.DataPointFloat.value))).where(
                    models.DataPointFloat.datasource_id == datasource_id
                )
            ).scalar()
            result["oldest_datetime"] = db.execute(
                select(models.DataPointFloat.datetime)
                .where(models.DataPointFloat.datasource_id == datasource_id)
                .order_by(models.DataPointFloat.datetime.asc())
                .limit(1)
            ).scalar()
            result["newest_datetime"] = db.execute(
                select(models.DataPointFloat.datetime)
                .where(models.DataPointFloat.datasource_id == datasource_id)
                .order_by(models.DataPointFloat.datetime.desc())
                .limit(1)
            ).scalar()

            # float specific
            result["type_specific"] = {}
            result["type_specific"]["mean"] = db.execute(
                select(func.avg(models.DataPointFloat.value)).where(
                    models.DataPointFloat.datasource_id == datasource_id
                )
            ).scalar()
            result["type_specific"]["std"] = db.execute(
                select(func.stddev(models.DataPointFloat.value)).where(
                    models.DataPointFloat.datasource_id == datasource_id
                )
            ).scalar()
            result["type_specific"]["min"] = db.execute(
                select(models.DataPointFloat.value)
                .where(models.DataPointFloat.datasource_id == datasource_id)
                .order_by(models.DataPointFloat.value.asc())
                .limit(1)
            ).scalar()
            result["type_specific"]["percentile_25"] = db.execute(
                select(func.percentile_disc(0.25).within_group(models.DataPointFloat.value.asc()))
                .where(models.DataPointFloat.datasource_id == datasource_id)
                .limit(1)
            ).scalar()
            result["type_specific"]["percentile_50"] = db.execute(
                select(func.percentile_disc(0.50).within_group(models.DataPointFloat.value.asc()))
                .where(models.DataPointFloat.datasource_id == datasource_id)
                .limit(1)
            ).scalar()
            result["type_specific"]["percentile_75"] = db.execute(
                select(func.percentile_disc(0.75).within_group(models.DataPointFloat.value.asc()))
                .where(models.DataPointFloat.datasource_id == datasource_id)
                .limit(1)
            ).scalar()
            result["type_specific"]["max"] = db.execute(
                select(models.DataPointFloat.value)
                .where(models.DataPointFloat.datasource_id == datasource_id)
                .order_by(models.DataPointFloat.value.desc())
                .limit(1)
            ).scalar()

            return result
        case "vector3":
            result = {}

            # common
            result["count"] = db.execute(
                select(func.count(models.DataPointVector3.datetime)).where(
                    models.DataPointVector3.datasource_id == datasource_id
                )
            ).scalar()
            result["count_distinct"] = db.execute(
                select(func.count(func.distinct(models.DataPointVector3.value))).where(
                    models.DataPointVector3.datasource_id == datasource_id
                )
            ).scalar()
            result["oldest_datetime"] = db.execute(
                select(models.DataPointVector3.datetime)
                .where(models.DataPointVector3.datasource_id == datasource_id)
                .order_by(models.DataPointVector3.datetime.asc())
                .limit(1)
            ).scalar()
            result["newest_datetime"] = db.execute(
                select(models.DataPointVector3.datetime)
                .where(models.DataPointVector3.datasource_id == datasource_id)
                .order_by(models.DataPointVector3.datetime.desc())
                .limit(1)
            ).scalar()

            # vector3 specific
            result["type_specific"] = {}
            result["type_specific"]["minX"] = db.execute(
                select(models.DataPointVector3.x)
                .where(models.DataPointVector3.datasource_id == datasource_id)
                .order_by(models.DataPointFloat.x.asc())
                .limit(1)
            ).scalar()
            result["type_specific"]["maxX"] = db.execute(
                select(models.DataPointVector3.x)
                .where(models.DataPointVector3.datasource_id == datasource_id)
                .order_by(models.DataPointFloat.x.desc())
                .limit(1)
            ).scalar()
            result["type_specific"]["minY"] = db.execute(
                select(models.DataPointVector3.y)
                .where(models.DataPointVector3.datasource_id == datasource_id)
                .order_by(models.DataPointFloat.y.asc())
                .limit(1)
            ).scalar()
            result["type_specific"]["maxY"] = db.execute(
                select(models.DataPointVector3.y)
                .where(models.DataPointVector3.datasource_id == datasource_id)
                .order_by(models.DataPointFloat.y.desc())
                .limit(1)
            ).scalar()
            result["type_specific"]["minZ"] = db.execute(
                select(models.DataPointVector3.z)
                .where(models.DataPointVector3.datasource_id == datasource_id)
                .order_by(models.DataPointFloat.z.asc())
                .limit(1)
            ).scalar()
            result["type_specific"]["maxZ"] = db.execute(
                select(models.DataPointVector3.z)
                .where(models.DataPointVector3.datasource_id == datasource_id)
                .order_by(models.DataPointFloat.z.desc())
                .limit(1)
            ).scalar()

            return result
        case "json":
            result = {}

            # common
            result["count"] = db.execute(
                select(func.count(models.DataPointJSON.datetime)).where(
                    models.DataPointJSON.datasource_id == datasource_id
                )
            ).scalar()
            result["count_distinct"] = db.execute(
                select(func.count(func.distinct(models.DataPointJSON.value))).where(
                    models.DataPointJSON.datasource_id == datasource_id
                )
            ).scalar()
            result["oldest_datetime"] = db.execute(
                select(models.DataPointJSON.datetime)
                .where(models.DataPointJSON.datasource_id == datasource_id)
                .order_by(models.DataPointJSON.datetime.asc())
                .limit(1)
            ).scalar()
            result["newest_datetime"] = db.execute(
                select(models.DataPointJSON.datetime)
                .where(models.DataPointJSON.datasource_id == datasource_id)
                .order_by(models.DataPointJSON.datetime.desc())
                .limit(1)
            ).scalar()

            return result


def get_datasource_stats_bulk(db: Session, datasource_ids: List[UUID]):
    data = []
    for datasource_id in datasource_ids:
        data.append({"datasource_id": datasource_id, "stats": get_datasource_stats(db=db, datasource_id=datasource_id)})
    return data


def create_datapoint(db: Session, datasource_id: UUID, datapoint: schemas.DataPointCreateUnion):
    db_datasource = db.query(models.DataSource).filter(models.DataSource.id == datasource_id).first()
    if not db_datasource:
        raise HTTPException(status_code=404, detail="Datasource not found.")

    match db_datasource.type:
        case "float":
            db_datapoint = models.DataPointFloat(**datapoint.dict(), datasource_id=datasource_id)
        case "vector3":
            db_datapoint = models.DataPointVector3(**datapoint.dict(), datasource_id=datasource_id)
        case "json":
            db_datapoint = models.DataPointJSON(**datapoint.dict(), datasource_id=datasource_id)

    db.add(db_datapoint)
    try:
        db.commit()
    except IntegrityError as error:
        if isinstance(error, CheckViolation):
            raise HTTPException(status_code=400, detail="JSON payload is not valid according to constraint")
        elif isinstance(error, UniqueViolation):
            match db_datasource.type:
                case "float":
                    db_datapoint = (
                        db.query(models.DataPointFloat)
                        .filter(
                            models.DataPointFloat.datasource_id == datasource_id,
                            models.DataPointFloat.datetime == datapoint.datetime,
                        )
                        .first()
                    )
                    db_datapoint.value = datapoint.value
                    db.add(db_datapoint)
                    db.commit()
                case "vector3":
                    db_datapoint = (
                        db.query(models.DataPointVector3)
                        .filter(
                            models.DataPointVector3.datasource_id == datasource_id,
                            models.DataPointVector3.datetime == datapoint.datetime,
                        )
                        .first()
                    )
                    db_datapoint.x = datapoint.x
                    db_datapoint.y = datapoint.y
                    db_datapoint.z = datapoint.z
                    db.add(db_datapoint)
                    db.commit()
                case "json":
                    db_datapoint = (
                        db.query(models.DataPointJSON)
                        .filter(
                            models.DataPointJSON.datasource_id == datasource_id,
                            models.DataPointJSON.datetime == datapoint.datetime,
                        )
                        .first()
                    )
                    db_datapoint.payload = datapoint.payload
                    db.add(db_datapoint)
                    db.commit()
        else:
            raise error
    db.refresh(db_datapoint)
    return db_datapoint


def create_datapoint_bulk(db: Session, datasource_id: UUID, datapoints: List[schemas.DataPointCreateUnion]):
    db_datasource = db.query(models.DataSource).filter(models.DataSource.id == datasource_id).first()
    if not db_datasource:
        raise HTTPException(status_code=404, detail="Datasource not found.")

    datapoint_dicts = [x.dict() for x in datapoints]
    for point in datapoint_dicts:
        point.update(datasource_id=datasource_id)

    match db_datasource.type:
        case "float":
            stmt = insert(models.DataPointFloat).values(datapoint_dicts)
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=["datetime", "datasource_id"],
                set_={
                    "value": stmt.excluded.value,
                },
            )
        case "vector3":
            stmt = insert(models.DataPointVector3).values(datapoint_dicts)
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=["datetime", "datasource_id"],
                set_={
                    "x": stmt.excluded.x,
                    "y": stmt.excluded.y,
                    "z": stmt.excluded.z,
                },
            )
        case "json":
            stmt = insert(models.DataPointJSON).values(datapoint_dicts)
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=["datetime", "datasource_id"],
                set_={
                    "payload": stmt.excluded.payload,
                },
            )

    db.execute(upsert_stmt)
    db.commit()


def create_mapping(user: models.User, model_id: UUID, datasource_id: UUID, object: str):
    return insert_edge(user=user, repo_id=model_id, obj=datasource_id, pred="dtlab:mapping", sub=object)


def delete_mapping(user: models.User, model_id: UUID, datasource_id: UUID, object: str):
    return delete_edge(user=user, repo_id=model_id, obj=datasource_id, pred="dtlab:mapping", sub=object)
