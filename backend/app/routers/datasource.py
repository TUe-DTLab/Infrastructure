import csv
from typing import List
from uuid import UUID

import pandas as pd
import sqlalchemy
from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from sqlalchemy.orm import Session

import app.crud.datasource as crud_datasource
from app import models, schemas
from app.dependencies import GetDatabase, current_active_user

router = APIRouter(tags=["Data sources"])


@router.post("/datasources/", response_model=schemas.DataSourceUnion)
def create(
    datasource: schemas.DataSourceCreateUnion,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    db_datasource = crud_datasource.create_datasource(db=db, datasource=datasource)

    crud_datasource.create_datasource_graph(user=user, datasource_id=db_datasource.id, datasource=datasource)

    return db_datasource


@router.delete("/datasources/{datasource_id}/", response_model=schemas.DataSourceUnion)
def delete(
    datasource_id: UUID, db: Session = Depends(GetDatabase(None)), user: models.User = Depends(current_active_user)
):
    db_datasource = crud_datasource.delete_datasource(db=db, datasource_id=datasource_id)

    crud_datasource.delete_datasource_graph(user=user, model_id=db_datasource.model_id, datasource_id=db_datasource.id)

    return db_datasource


@router.patch("/datasources/{datasource_id}/", response_model=schemas.DataSourceUnion)
def patch(
    datasource_id: UUID,
    datasource: schemas.DataSourceUpdateUnion,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    db_datasource = crud_datasource.update_datasource(db=db, datasource_id=datasource_id, datasource=datasource)

    crud_datasource.update_datasource_graph(
        user=user, model_id=db_datasource.model_id, datasource_id=datasource_id, datasource=datasource
    )

    return db_datasource


@router.get("/datasources/{datasource_id}/datapoints/", response_model=List[schemas.DataPointUnion])
def list_datapoints(
    datasource_id: UUID,
    query: schemas.Query = Depends(),
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    # validate input
    if query.aggregate_bucket and not query.aggregate_function:
        raise HTTPException(400, "Must specify aggregation function if using aggregation")
    if query.aggregate_function and not query.aggregate_bucket:
        raise HTTPException(400, "Must specify aggregation bucket if using aggregation")

    data = crud_datasource.query_datasource(db=db, datasource_id=datasource_id, query=query)

    if data[0].isinstance(sqlalchemy.engine.row.Row):
        data = [{"datetime": point[0], "value": point[1]} for point in data]

    return data


@router.post("/datasources/query/")
def bulk_query(
    query: schemas.QueryBulk,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    # validate input
    if query.query.aggregate_bucket and not query.query.aggregate_function:
        raise HTTPException(400, "Must specify aggregation function if using aggregation")
    if query.query.aggregate_function and not query.query.aggregate_bucket:
        raise HTTPException(400, "Must specify aggregation bucket if using aggregation")

    return crud_datasource.query_bulk_datasource(db=db, query=query)


@router.post("/datasources/{datasource_id}/datapoints/", response_model=schemas.DataPointUnion)
def create_datapoint(
    datasource_id: UUID,
    datapoint: schemas.DataPointCreateUnion,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    return jsonable_encoder(crud_datasource.create_datapoint(db=db, datasource_id=datasource_id, datapoint=datapoint))


@router.post("/datasources/{datasource_id}/bulk/")
def create_datapoints_bulk(
    datasource_id: UUID,
    file: UploadFile,
    datetime_column_name: str = "datetime",
    value_column_name: str = "value",
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    # accept csv / xlsx
    match file.content_type:
        case "text/csv":
            dialect = csv.Sniffer().sniff(str(file.file.readline(1024)))
            file.file.seek(0)
            df = pd.read_csv(file.file, sep=dialect.delimiter)
            df = df.drop_duplicates(datetime_column_name)
            data = []
            for row in df.iterrows():
                data.append(
                    schemas.DataPointFloatCreate(datetime=row[1][datetime_column_name], value=row[1][value_column_name])
                )
            crud_datasource.create_datapoint_bulk(db=db, datasource_id=datasource_id, datapoints=data)
        case "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(file.file)
            df = df.drop_duplicates(datetime_column_name)
            data = []
            for row in df.iterrows():
                data.append(
                    schemas.DataPointFloatCreate(datetime=row[1][datetime_column_name], value=row[1][value_column_name])
                )
            crud_datasource.create_datapoint_bulk(db=db, datasource_id=datasource_id, datapoints=data)


@router.post("/datasources/bulk/")
def update_datasources_bulk(
    model_id: UUID,
    file: UploadFile,
    datetime_column_name: str = "datetime",
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    # accept xlsx / csv
    match file.content_type:
        case "text/csv":
            dialect = csv.Sniffer().sniff(str(file.file.readline(1024)))
            file.file.seek(0)
            df = pd.read_csv(file.file, sep=dialect.delimiter)
            df = df.drop_duplicates(datetime_column_name)
            for col in df.columns:
                if col != datetime_column_name:
                    # get or create datasource
                    db_datasource = crud_datasource.get_datasource_by_name(db=db, model_id=model_id, name=col)
                    if db_datasource is None:
                        db_datasource = crud_datasource.create_datasource(
                            db=db,
                            datasource=schemas.DataSourceFloatCreate(
                                name=col, type=models.DataSourceEnum.float, model_id=model_id
                            ),
                        )

                    # insert data
                    data = []
                    for row in df.iterrows():
                        data.append(
                            schemas.DataPointFloatCreate(datetime=row[1][datetime_column_name], value=row[1][col])
                        )
                    crud_datasource.create_datapoint_bulk(db=db, datasource_id=db_datasource.id, datapoints=data)
        case "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(file.file)
            df = df.drop_duplicates(datetime_column_name)
            for col in df.columns:
                if col != datetime_column_name:
                    # get or create datasource
                    db_datasource = crud_datasource.get_datasource_by_name(db=db, model_id=model_id, name=col)
                    if db_datasource is None:
                        db_datasource = crud_datasource.create_datasource(
                            db=db,
                            datasource=schemas.DataSourceFloatCreate(
                                name=col, type=models.DataSourceEnum.float, model_id=model_id
                            ),
                        )

                    # insert data
                    data = []
                    for row in df.iterrows():
                        data.append(
                            schemas.DataPointFloatCreate(datetime=row[1][datetime_column_name], value=row[1][col])
                        )
                    crud_datasource.create_datapoint_bulk(db=db, datasource_id=db_datasource.id, datapoints=data)


@router.post("/datasources/stats/")
def stats_bulk(
    datasource_ids: List[UUID],
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    return crud_datasource.get_datasource_stats_bulk(db=db, datasource_ids=datasource_ids)


@router.get("/datasources/{datasource_id}/stats/")
def stats_datapoints(
    datasource_id: UUID,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    return crud_datasource.get_datasource_stats(db=db, datasource_id=datasource_id)


@router.post("/datasources/{datasource_id}/mapping/")
def create_mapping(
    datasource_id: UUID,
    model_id: UUID,
    object: str,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    return crud_datasource.create_mapping(user=user, model_id=model_id, datasource_id=datasource_id, object=object)


@router.delete("/datasources/{datasource_id}/mapping/")
def delete_mapping(
    datasource_id: UUID,
    model_id: UUID,
    object: str,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_active_user),
):
    return crud_datasource.delete_mapping(user=user, model_id=model_id, datasource_id=datasource_id, object=object)
