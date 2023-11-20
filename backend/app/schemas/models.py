from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ModelBase(BaseModel):
    pass


class ModelCreate(BaseModel):
    name: str
    public: bool = False


class ModelUpdate(BaseModel):
    name: Optional[str]
    public: Optional[str]


class Model(ModelBase):
    id: UUID
    public: bool

    class Meta:
        orm_mode = True
