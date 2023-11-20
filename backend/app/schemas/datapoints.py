import datetime
from typing import Dict, Union

from pydantic import BaseModel


class DataPointFloatBase(BaseModel):
    datetime: datetime.datetime
    value: float


class DataPointFloatCreate(DataPointFloatBase):
    pass


class DataPointFloat(DataPointFloatBase):
    # datasource_id: UUID

    class Meta:
        orm_mode = True


class DataPointVector3Base(BaseModel):
    datetime: datetime.datetime
    x: float
    y: float
    z: float


class DataPointVector3Create(DataPointVector3Base):
    pass


class DataPointVector3(DataPointVector3Base):
    # datasource_id: UUID

    class Meta:
        orm_mode = True


class DataPointJSONBase(BaseModel):
    datetime: datetime.datetime
    payload: Dict


class DataPointJSONCreate(DataPointJSONBase):
    pass


class DataPointJSON(DataPointJSONBase):
    # datasource_id: UUID

    class Meta:
        orm_mode = True


DataPointCreateUnion = Union[DataPointFloatCreate, DataPointVector3Create, DataPointJSONCreate]
DataPointUnion = Union[DataPointFloat, DataPointVector3, DataPointJSON]
