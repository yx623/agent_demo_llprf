import httpx
import pytest

from app.main import app


@pytest.mark.anyio
async def test_health_endpoint():
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert "status" in response.json()


@pytest.mark.anyio
async def test_resume_endpoint():
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        run_response = await client.post(
            "/tasks/run",
            json={
                "user_id": "demo-user",
                "title": "解释 LangGraph",
                "input_text": "请写一份 LangGraph 教学提纲",
            },
        )
        run_id = run_response.json()["run_id"]

        response = await client.post(f"/tasks/{run_id}/resume")

    assert response.status_code == 200
    assert response.json()["run_id"] == run_id
