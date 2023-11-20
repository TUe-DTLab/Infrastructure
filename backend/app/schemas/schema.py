from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class SchemaBase(BaseModel):
    name: str
    json_schema: Dict


class SchemaCreate(SchemaBase):
    pass


class SchemaUpdate(BaseModel):
    name: Optional[str]
    json_schema: Optional[Dict]


class Schema(SchemaBase):
    id: UUID

    class Config:
        orm_mode = True
