import uuid
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr

from app.models import RoleEnum


class UserName(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class RoleBase(BaseModel):
    role: RoleEnum
    user_id: UUID


class RoleBaseProject(RoleBase):
    project_id: UUID


class RoleBaseModel(RoleBase):
    model_id: UUID


class RoleCreateProject(RoleBaseProject):
    pass


class RoleCreateModel(RoleBaseModel):
    pass


class RoleDeleteProject(BaseModel):
    project_id: UUID
    user_id: UUID


class RoleDeleteModel(BaseModel):
    model_id: UUID
    user_id: UUID


class RoleUpdateProject(RoleBaseProject):
    pass


class RoleUpdateModel(RoleBaseModel):
    user_id: UUID


class RoleProject(RoleBaseProject):
    class Config:
        orm_mode = True


class RoleModel(RoleBaseModel):
    user_id: UUID
    role: str

    class Config:
        orm_mode = True


class UserRead(schemas.BaseUser[uuid.UUID]):
    created_at: datetime
    updated_at: datetime

    project_roles: List[RoleProject]
    model_roles: List[RoleModel]

    user_data: Optional[dict]


class UserCreate(schemas.CreateUpdateDictModel):
    email: EmailStr
    password: str

    user_data: Optional[dict]


class UserUpdate(schemas.BaseUserUpdate):
    user_data: Optional[dict]
