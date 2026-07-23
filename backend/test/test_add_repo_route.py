import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient, ASGITransport

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
async def test_list_installation_repos_missing_installation_id(client):
    response = await client.get("/installation-repos")
    assert response.status_code == 400 
    assert response.json() == {"error": "GitHub App not installed or installation_id missing"}

@pytest.mark.asyncio
async def test_list_installation_repos_success(client):
    with patch("routes.add_repo_route.get_repos_from_installation",
               return_value = {"repositories":[{"name":"repo-one"},{"name":"repo-two"}]}):

        response = await client.get(
            "/installation-repos",
            cookies={"installation_id":"fake_id_123"}
            )
        
    assert response.status_code == 200
    assert len(response.json()["repositories"]) == 2
    assert response.json()["repositories"][0]["name"] == "repo-one"

@pytest.mark.asyncio
async def test_list_installation_repos_exception(client):
    with patch("routes.add_repo_route.get_repos_from_installation",
               side_effect=Exception("GitHub down")):
        # ↑ side_effect forces an exception to be raised

        response = await client.get(
            "/installation-repos",
            cookies={"installation_id": "fake_id_123"}
        )

    assert response.status_code == 500
    assert response.json() == {"error": "Failed to fetch repositories"}

@pytest.mark.asyncio
async def test_branches_name_missing_installation_id(client):
    response = await client.get(
        "/branches/repo-one",
        params={"owner": "owner-one"},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "No installation ID"}

@pytest.mark.asyncio
async def test_branches_name_success(client):
    gh = AsyncMock()
    gh.__aenter__.return_value = gh
    gh.list_branches.return_value = [{"name": "branch-one"}, {"name": "branch-two"}]

    with patch("routes.add_repo_route.GitHubMCP.for_installation",
               AsyncMock(return_value=gh)):

        response = await client.get(
            "/branches/repo-one",
            params={"owner": "owner-one"},
            cookies={"installation_id": "fake_id_123"},
        )

        assert response.status_code == 200
        assert len(response.json()["Branches"]) == 2
        assert response.json()["Branches"][0]["name"] == "branch-one"

@pytest.mark.asyncio
async def test_branches_exception(client):
    with patch("routes.add_repo_route.GitHubMCP.for_installation",
               AsyncMock(side_effect=Exception("GitHub down"))):

        response = await client.get(
            "/branches/repo-one",
            params={"owner": "owner-one"},
            cookies={"installation_id": "fake_id_123"},
        )

    assert response.status_code == 500
    assert response.json() == {"error": "Failed to fetch repositories"}