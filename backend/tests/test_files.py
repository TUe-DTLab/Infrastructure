import filecmp
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app as fastapiapp
from tests.conftest import InitialState

pytest_plugins = ("pytest_asyncio",)


@pytest_asyncio.fixture()
async def upload_file(setup_session, get_bearer_token):
    file_name = "test_file.csv"
    file = Path("tests/media", file_name)
    data = {"file": (file_name, open(file, "rb"), "multipart/form-data")}
    params = {"file_name": file_name}

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.post(
            f"/projects/{InitialState.project.id}/files/", params=params, files=data, headers=get_bearer_token
        )
    assert response.status_code == 200
    yield response.json()["id"]
    p = Path("media", str(InitialState.project.id))
    for item in p.iterdir():
        Path.unlink(item)
    p.rmdir()


@pytest.mark.asyncio
async def test_upload_file(setup_session, get_bearer_token, upload_file):
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get(f"/projects/{InitialState.project.id}/files/", headers=get_bearer_token)
    file_name = "test_file.csv"
    path = Path("media", str(InitialState.project.id), file_name)
    assert response.status_code == 200
    assert any("test_file.csv" == sub["name"] for sub in response.json())
    assert filecmp.cmp(path, Path("tests/media", file_name))
    Path.unlink(path)


@pytest.mark.asyncio
async def test_list_files(setup_session, get_bearer_token, upload_file):
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get(f"/projects/{InitialState.project.id}/files/", headers=get_bearer_token)
    file_name = "test_file.csv"
    path = Path("media", str(InitialState.project.id), file_name)
    assert response.status_code == 200
    assert any("test_file.csv" == sub["name"] for sub in response.json())
    assert filecmp.cmp(path, Path("tests/media", file_name))
    Path.unlink(path)


@pytest.mark.asyncio
async def test_delete_file(setup_session, get_bearer_token, upload_file):
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get(f"/projects/{InitialState.project.id}/files/", headers=get_bearer_token)

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.delete(f"/files/{upload_file}/", headers=get_bearer_token)
    file_name = "test_file.csv"
    path = Path("media", file_name)
    assert response.status_code == 200
    assert not path.exists()


@pytest.mark.asyncio
async def test_new_file_new_name(setup_session, get_bearer_token, upload_file):
    file_name = "test_file2.csv"
    file = Path("tests/media", file_name)
    data = {"file": (file_name, open(file, "rb"), "multipart/form-data")}
    params = {"file_name": file_name}

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.patch(
            f"/files/{upload_file}/",
            params=params,
            files=data,
            headers=get_bearer_token,
        )

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get(f"/projects/{InitialState.project.id}/files/", headers=get_bearer_token)
    path = Path("media", str(InitialState.project.id), file_name)
    print(response.text)
    assert response.status_code == 200
    assert any(file_name == sub["name"] for sub in response.json())
    assert filecmp.cmp(path, Path("tests/media", file_name))


@pytest.mark.asyncio
async def test_old_file_new_name(setup_session, get_bearer_token, upload_file):
    new_file_name = "test_file2.csv"
    file_name = "test_file.csv"
    # data = "file="
    params = {"file_name": new_file_name}

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.patch(
            f"/files/{upload_file}/",
            params=params,
            headers=get_bearer_token,
        )

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get(f"/projects/{InitialState.project.id}/files/", headers=get_bearer_token)
    path = Path("media", str(InitialState.project.id), new_file_name)
    assert response.status_code == 200
    assert any(new_file_name == sub["name"] for sub in response.json())
    assert filecmp.cmp(path, Path("tests/media", file_name))


@pytest.mark.asyncio
async def test_new_file_old_name(setup_session, get_bearer_token, upload_file):
    old_file_name = "test_file.csv"
    file_name = "test_file2.csv"
    file = Path("tests/media", file_name)
    data = {"file": (file_name, open(file, "rb"), "multipart/form-data")}

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.patch(
            f"/files/{upload_file}/",
            files=data,
            headers=get_bearer_token,
        )

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get(f"/projects/{InitialState.project.id}/files/", headers=get_bearer_token)
    path = Path("media", str(InitialState.project.id), old_file_name)
    print(response.text)
    assert response.status_code == 200
    assert any(old_file_name == sub["name"] for sub in response.json())
    assert filecmp.cmp(path, Path("tests/media", file_name))


@pytest.mark.asyncio
async def test_reading_file(setup_session, get_bearer_token, upload_file):
    file_name = "test_file.csv"
    file = Path("tests/media", file_name)

    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.get(
            f"/files/{upload_file}/",
            headers=get_bearer_token,
        )
    with file.open() as f:
        assert response.text == f.read()
