from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ProjectBase(BaseModel):
    pass


class ProjectCreate(ProjectBase):
    name: str
    public: bool = False


class ProjectUpdate(BaseModel):
    name: Optional[str]
    public: Optional[bool]


class Project(ProjectBase):
    id: UUID
    public: bool

    class Config:
        orm_mode = True
