import enum
from datetime import datetime
from typing import List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from app.models import DataSourceEnum
from app.schemas.datapoints import DataPointUnion


class DataSourceBase(BaseModel):
    name: str
    type: DataSourceEnum
    model_id: UUID


class DataSourceFloatBase(DataSourceBase):
    type: Literal[DataSourceEnum.float]


class DataSourceFloatCreate(DataSourceFloatBase):
    pass


class DataSourceFloatUpdate(BaseModel):
    name: Optional[str]


class DataSourceFloat(DataSourceFloatBase):
    id: UUID

    class Config:
        orm_mode = True


class DataSourceVector3Base(DataSourceBase):
    type: Literal[DataSourceEnum.vector3]


class DataSourceVector3Create(DataSourceVector3Base):
    pass


class DataSourceVector3Update(BaseModel):
    name: Optional[str]


class DataSourceVector3(DataSourceVector3Base):
    id: UUID

    class Config:
        orm_mode = True


class DataSourceJSONBase(DataSourceBase):
    type: Literal[DataSourceEnum.json]
    schema_id: UUID


class DataSourceJSONCreate(DataSourceJSONBase):
    pass


class DataSourceJSONUpdate(BaseModel):
    name: Optional[str]
    schema_id: Optional[UUID]


class DataSourceJSON(DataSourceJSONBase):
    id: UUID

    class Config:
        orm_mode = True


DataSourceCreateUnion = Union[DataSourceFloatCreate, DataSourceVector3Create, DataSourceJSONCreate]
DataSourceUnion = Union[DataSourceFloat, DataSourceVector3, DataSourceJSON]
DataSourceUpdateUnion = Union[DataSourceFloatUpdate, DataSourceVector3Update, DataSourceJSONUpdate]


class AggregateFunctionEnum(enum.Enum):
    MEAN = "MEAN"
    STD = "STD"
    SUM = "SUM"
    MIN = "MIN"
    MAX = "MAX"
    COUNT = "COUNT"


class Query(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = 0
    limit: int = 1000
    time_ascending: bool = True
    aggregate_bucket: Optional[str] = None
    aggregate_function: Optional[AggregateFunctionEnum] = None


class QueryBulk(BaseModel):
    datasource_ids: List[UUID]
    query: Query


class QueryBulkResults(BaseModel):
    datasource_id: UUID
    results: List[DataPointUnion]
