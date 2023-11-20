import pytest

# import pytest_asyncio
from httpx import AsyncClient

from app.main import app as fastapiapp
from tests.conftest import InitialState

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_create_sensor(setup_session, get_bearer_token):
    data = {"name": "test-sensor", "project_id": str(InitialState.project.id)}
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.post("/sensors/", headers=get_bearer_token, json=data)
    assert response.status_code == 200
    assert response.json() != []
    assert response.json()["name"] == "test-sensor"


@pytest.mark.asyncio
async def test_list_sensor(setup_session, get_bearer_token):
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get("/sensors/", headers=get_bearer_token)
    assert response.status_code == 200
    assert response.json() != []
    assert any("initial-sensor" == sub["name"] for sub in response.json())


@pytest.mark.asyncio
async def test_delete_sensor(setup_session, get_bearer_token):
    print(InitialState.sensor.id)

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.delete(f"/sensors/{InitialState.sensor.id}/", headers=get_bearer_token)
    assert response.status_code == 200

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get("/sensors/", headers=get_bearer_token)
    assert response.status_code == 200
    assert not any("initial-sensor" == sub["name"] for sub in response.json())


@pytest.mark.asyncio
async def test_get_sensor_by_id(setup_session, get_bearer_token):
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get(f"/sensors/{InitialState.sensor.id}/", headers=get_bearer_token)
    print(response.json())
    assert response.status_code == 200
    assert response.json() != []
    assert response.json()["id"] == InitialState.sensor.id
    assert response.json()["name"] == "initial-sensor"
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_sensor_data_by_id(setup_session, get_bearer_token):
    data = {"datetime": "2022-09-01T08:26:30.202Z", "value": 0}
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.post(f"/sensors/{InitialState.sensor.id}/data/", json=data, headers=get_bearer_token)
    print(response.json())
    assert response.status_code == 200
    assert response.json()["sensor_id"] == InitialState.sensor.id
    assert response.json()["datetime"] == "2022-09-01T08:26:30.202000"
    assert response.json()["value"] == 0


@pytest.mark.asyncio
async def test_read_sensor_data_by_id(setup_session, get_bearer_token):
    data = {"datetime": "2022-09-01T08:26:30.202Z", "value": 0}
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.post(f"/sensors/{InitialState.sensor.id}/data/", json=data, headers=get_bearer_token)

    print(response.json())
    assert response.status_code == 200

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get(f"/sensors/{InitialState.sensor.id}/data/", headers=get_bearer_token)
    print(response.json())
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_edit_sensor(setup_session, get_bearer_token):
    data = {"name": "new-test-sensor"}
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.patch(f"/sensors/{InitialState.sensor.id}/", headers=get_bearer_token, json=data)
    assert response.status_code == 200
    assert response.json() != []
    assert response.json()["name"] == "new-test-sensor"
