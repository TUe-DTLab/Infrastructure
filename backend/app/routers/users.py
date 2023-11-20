from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

import app.crud.users as crud_users
from app import models, schemas
from app.dependencies import GetDatabase, current_user_admin

router = APIRouter(tags=["Users"])


@router.get("/users/", response_model=List[schemas.UserRead])
def list_users(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(GetDatabase(None)),
    user: models.User = Depends(current_user_admin),
):
    return crud_users.get_users(db=db, skip=skip, limit=limit)
