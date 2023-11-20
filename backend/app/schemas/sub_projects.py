from typing import Optional

from pydantic import BaseModel


class SubProjectBIMBase(BaseModel):
    project_id: int
    ifc_file_id: Optional[int]
    ttl_file_id: Optional[int]


class SubProjectBIMCreate(SubProjectBIMBase):
    pass


class SubProjectBIM(SubProjectBIMBase):
    class Config:
        orm_mode = True
