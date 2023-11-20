import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app as fastapiapp

pytest_plugins = ("pytest_asyncio",)


@pytest_asyncio.fixture()
async def create_project(setup_session, get_bearer_token):
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.post("/projects/", json={"name": "test-project"}, headers=get_bearer_token)
    assert response.status_code == 200
    assert response.json() != []
    assert response.json()["name"] == "test-project"
    assert "id" in response.json()
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_project(setup_session, get_bearer_token, create_project):
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get("/projects/", headers=get_bearer_token)
    assert response.status_code == 200
    assert response.json() != []
    assert any("test-project" == sub["name"] for sub in response.json())


@pytest.mark.asyncio
async def test_get_project_by_id(setup_session, get_bearer_token, create_project):
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get(f"/projects/{create_project}/", headers=get_bearer_token)
    assert response.status_code == 200
    assert response.json() != []
    assert response.json()["id"] == create_project
    assert response.json()["name"] == "test-project"


@pytest.mark.asyncio
async def test_list_projects(setup_session, get_bearer_token):
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get("/projects/", headers=get_bearer_token)
    assert response.status_code == 200
    assert response.json() != []
    assert any("initial-project" == sub["name"] for sub in response.json())


@pytest.mark.asyncio
async def test_delete_project(setup_session, get_bearer_token, create_project):
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.delete(f"/projects/{create_project}/", headers=get_bearer_token)
    assert response.status_code == 200

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get("/projects/", headers=get_bearer_token)
    assert response.status_code == 200
    assert not any("test-project" == sub["name"] for sub in response.json())


@pytest.mark.asyncio
async def test_modify_project_by_id(setup_session, get_bearer_token, create_project):
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get(f"/projects/{create_project}/", headers=get_bearer_token)
    assert response.status_code == 200
    assert response.json() != []
    assert response.json()["id"] == create_project
    assert response.json()["name"] == "test-project"
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.patch(
            f"/projects/{create_project}/",
            json={"name": "modified-project-name"},
            headers=get_bearer_token,
        )

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get(f"/projects/{create_project}/", headers=get_bearer_token)
    assert response.status_code == 200
    assert response.json() != []
    assert response.json()["id"] == create_project
    assert response.json()["name"] == "modified-project-name"
