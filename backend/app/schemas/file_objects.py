from typing import Optional
from uuid import UUID

from fastapi import UploadFile
from pydantic import BaseModel


class FileObjectBase(BaseModel):
    name: str


class FileObjectCreate(FileObjectBase):
    model_id: UUID


class FileObjectUpdate(BaseModel):
    name: Optional[str]
    file: Optional[UploadFile]


class FileObject(FileObjectBase):
    id: UUID
    model_id: UUID

    class Config:
        orm_mode = True
