from fastapi import APIRouter

router = APIRouter(tags=["MQTT"])


# Client handling
@router.get("/models/{model_id}/mqtt/clients/")
def list_clients():
    pass


@router.post("/models/{model_id}/mqtt/clients/")
def create_client():
    pass


@router.get("/models/{model_id}/mqtt/clients/{client_id}/")
def get_client():
    pass


@router.patch("/models/{model_id}/mqtt/clients/{client_id}/")
def update_client():
    pass


@router.delete("/models/{model_id}/mqtt/clients/{client_id}/")
def delete_client():
    pass


# Permissions handling
@router.get("/models/{model_id}/mqtt/clients/{client_id}/permissions/")
def get_permissions():
    pass


@router.post("/models/{model_id}/mqtt/clients/{client_id}/permissions/")
def create_permission():
    pass


@router.delete("/models/{model_id}/mqtt/clients/{client_id}/permissions/")
def delete_permission():
    pass


# Topic handling
@router.post("/models/{model_id}/topics/")
def create_topic():
    pass


@router.patch("/models/{model_id}/topics/{topic_id}/")
def update_topic():
    pass


@router.delete("/models/{model_id}/topics/{topic_id}/")
def delete_topic():
    pass
