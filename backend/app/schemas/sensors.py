import uuid
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel


class SensorReadingBase(BaseModel):
    datetime: datetime
    value: float


class SensorReadingCreate(SensorReadingBase):
    pass


class SensorReading(SensorReadingBase):
    sensor_id: int

    class Config:
        orm_mode = True


class SensorBase(BaseModel):
    name: str
    project_id: int
    mesh_ids: Optional[List[uuid.UUID]]


class SensorCreate(SensorBase):
    pass


class SensorUpdate(BaseModel):
    name: Union[str, None] = None
    project_id: Union[int, None] = None
    mesh_ids: Union[List[uuid.UUID], None] = None


class Sensor(SensorBase):
    id: int

    class Config:
        orm_mode = True


class SensorFull(Sensor):
    data: List[SensorReading] = []
