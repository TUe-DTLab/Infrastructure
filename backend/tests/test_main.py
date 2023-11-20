import pytest
from httpx import AsyncClient

from app.main import app

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://localhost") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
