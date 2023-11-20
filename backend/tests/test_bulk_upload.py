from pathlib import Path

import pytest

# import pytest_asyncio
from httpx import AsyncClient

from app.main import app as fastapiapp
from tests.conftest import InitialState

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_bulk_csv(setup_session, get_bearer_token):
    file_name = "test_bulk.csv"
    file = Path("tests/media", file_name)
    data = {"file": (file_name, open(file, "rb"), "multipart/form-data")}
    params = {"file_name": file_name}
    sensor_names = [
        "08BEAC0A1BFE_t",
        "08BEAC0A1BFE_h",
        "08BEAC0A1BFE_pm25",
        "08BEAC0A1BFE_pm10",
        "08BEAC0A1BFE_hcho",
        "08BEAC0A1BFE_tvoc",
        "08BEAC0A1BFE_co2",
        "08BEAC0A1BFE_co",
    ]

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.post(
            f"/projects/{InitialState.project.id}/bulk_csv/", params=params, files=data, headers=get_bearer_token
        )
    print(response.json())
    assert response.status_code == 200

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get("/sensors/", headers=get_bearer_token)
    print(response.json())
    assert response.status_code == 200
    for sensor in sensor_names:
        assert any(sensor == sub["name"] for sub in response.json())


@pytest.mark.asyncio
async def test_bulk_xlsx(setup_session, get_bearer_token):
    file_name = "test_bulk.xlsx"
    file = Path("tests/media", file_name)
    data = {"file": (file_name, open(file, "rb"), "multipart/form-data")}
    params = {"file_name": file_name}
    sensor_names = [
        "08BEAC0A1BFE_t",
        "08BEAC0A1BFE_h",
        "08BEAC0A1BFE_pm25",
        "08BEAC0A1BFE_pm10",
        "08BEAC0A1BFE_hcho",
        "08BEAC0A1BFE_tvoc",
        "08BEAC0A1BFE_co2",
        "08BEAC0A1BFE_co",
    ]

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.post(
            f"/projects/{InitialState.project.id}/bulk_xlsx/", params=params, files=data, headers=get_bearer_token
        )
    print(response.json())
    assert response.status_code == 200

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get("/sensors/", headers=get_bearer_token)
    print(response.json())
    assert response.status_code == 200
    for sensor in sensor_names:
        assert any(sensor == sub["name"] for sub in response.json())
