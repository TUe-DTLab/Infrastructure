import os
from pathlib import Path
from typing import List, Union

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app import models
from app.config import config
from app.dependencies import get_async_db

router = APIRouter(tags=["3D Tiles"])


@router.get("/3dtiles/{dataset:str}/{filepath:path}")
async def tileset(
    dataset: str,
    filepath: str,
    user_id_header: Union[str, None] = Header(default=None),
    user_id: Union[str, None] = None,
    db: Session = Depends(get_async_db),
):
    # TODO: do proper authentication
    # for now using uuid is sufficient + verified user

    if not user_id and not user_id_header:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if user_id:
        stmt = select(models.User).where(models.User.id == user_id)
    else:
        stmt = select(models.User).where(models.User.id == user_id_header)

    try:
        user = await db.execute(stmt)
    except Exception:
        raise HTTPException(status_code=403, detail="Unauthorized")
    user = user.unique().fetchall()
    if user == [] or not user[0][0].is_verified:
        raise HTTPException(status_code=403, detail="Unauthorized")

    path_root = Path(config["TILESET_ROOT"])

    # check dataset is a folder in tileset root
    if not any([name == dataset for name in os.listdir(path_root) if os.path.isdir(path_root / name)]):
        raise HTTPException(status_code=404, detail="Dataset {} not found".format(dataset))

    path_root = path_root / dataset

    filepath_obj = Path(filepath)
    filepath_abs = Path(filepath_obj._flavour.pathmod.normpath(str(path_root / filepath_obj)))

    try:
        filepath_abs.relative_to(path_root)
    except ValueError:
        raise HTTPException(status_code=404, detail="{} wrt {} is impossible".format(filepath_abs, path_root))

    if config["NGINX"] == "True":
        # see https://www.nginx.com/resources/wiki/start/topics/examples/xsendfile/
        response = Response()
        response.headers["X-Accel-Redirect"] = config["TILESET_BASE_URL"] + dataset + "/" + filepath
        return response
    else:
        return FileResponse(filepath_abs)


@router.post("/3dtiles_obj/eindhoven/")
def obj(coords: List[tuple[int, int]]):
    print(coords)
    return
