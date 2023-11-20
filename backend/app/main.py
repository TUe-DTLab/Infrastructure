from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import schemas
from app.config import config
from app.dependencies import auth_backend, fastapi_users
from app.routers import (
    data_conversion,
    datasource,
    file_objects,
    model_content,
    models,
    mqtt,
    projects,
    roles,
    schema,
    tiles3d,
    users,
)

app = FastAPI(
    root_path=config["ROOT_PATH"],
    version=str(config["MAJOR"]) + "." + str(config["MINOR"]) + "." + str(config["PATCH"]),
)

origins = config["CORS_ORIGINS"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["Auth"])
app.include_router(
    fastapi_users.get_register_router(schemas.UserRead, schemas.UserCreate),
    prefix="/auth",
    tags=["Auth"],
)
app.include_router(
    fastapi_users.get_users_router(schemas.UserRead, schemas.UserUpdate),
    prefix="/users",
    tags=["Users"],
)

app.include_router(roles.router_model)
app.include_router(roles.router_project)
app.include_router(projects.router)
app.include_router(file_objects.router)
app.include_router(tiles3d.router)
app.include_router(datasource.router)
app.include_router(schema.router)
app.include_router(models.router)
app.include_router(model_content.router)
app.include_router(data_conversion.router)
app.include_router(mqtt.router)
app.include_router(users.router)


@app.get("/info", response_model=schemas.Info)
def read_root():
    return {
        "version": str(config["MAJOR"]) + "." + str(config["MINOR"]) + "." + str(config["PATCH"]),
        "ontology_version": str(config["ONTOLOGY_VERSION_MAJOR"])
        + "."
        + str(config["ONTOLOGY_VERSION_MINOR"])
        + "."
        + str(config["ONTOLOGY_VERSION_PATCH"]),
        "ontology_base_url": config["ONTOLOGY_BASE_URL"],
    }
