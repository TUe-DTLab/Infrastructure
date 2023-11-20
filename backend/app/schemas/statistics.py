from datetime import datetime
from typing import Union

from pydantic import BaseModel


class StatisticsFloat(BaseModel):
    mean: float
    std: float
    min: float
    percentile_25: float
    percentile_50: float
    percentile_75: float
    max: float


class StatisticsVector3(BaseModel):
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float


class StatisticsJSON(BaseModel):
    pass


StatisticsUnion = Union[StatisticsFloat, StatisticsVector3, StatisticsJSON]


class Statistics(BaseModel):
    oldest_datetime: datetime
    newest_datetime: datetime
    count: int
    count_unique: int
    data_type: StatisticsUnion
