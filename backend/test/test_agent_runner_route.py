from datetime import datetime
from starlette.testclient import TestClient
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
import server
from models.agent_model import AgentMessage, JobStatus, JobStatusResponse, RoleType

with patch("services.ws.JobConnectionManager", MagicMock()):
    import server

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=server.app),
        base_url="http://test"
    ) as ac:
        yield ac

@pytest.mark.asyncio
async def test_run_agent_success(client):
    with patch("routes.agent_runner_routes.schedule_agent_job",
               return_value="fake_job_id_123"):

        response = await client.post(
            "/agent/run",
            json={
                "prompt": "fix the bug",
                "repo_name": "my-repo",
                "installation_id": 999,
                "branches": "main"
            }
            # ↑ RunAgentRequest fields — all required
        )

    assert response.status_code == 200
    assert response.json()["job_id"] == "fake_job_id_123"
    assert response.json()["status"] == "queued"

@pytest.mark.asyncio
async def test_run_agent_missing_field(client):
    response = await client.post(
        "/agent/run",
        json={
            "prompt": "fix the bug"
            }
        )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_agent_status_not_found(client):

    with patch("routes.agent_runner_routes.get_job_status", return_value=None), \
         patch("routes.agent_runner_routes.redisservices.get_job_status",
               return_value=None):

        response = await client.get("/agent/status/nonexistent_job")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

@pytest.mark.asyncio
async def test_get_agent_status_success(client):
        fake_status = JobStatusResponse(
            job_id="fake_job_id_123",
            status=JobStatus.RUNNING,
            messages=[
                AgentMessage(
                    role=RoleType.AGENT,
                    content="Working on it",
                    timestamp=datetime.now().isoformat()
                )
            ],
            file_changes=[],
            current_step="Analyzing code",
            created_at=datetime.now().isoformat()
        )
        
        with patch("routes.agent_runner_routes.get_job_status", return_value=fake_status):

            response = await client.get("/agent/status/fake_job_id_123")

            assert response.status_code == 200
            assert response.json()["job_id"] == "fake_job_id_123"
            assert response.json()["status"] == "running"

# --------------------------------------------------WEBSOCKET-TEST---------------------------------------------------------------

@pytest.mark.skip(reason="WebSocket handler has infinite loops — hard to test")
def test_websocket_connects_successfully():
    pass