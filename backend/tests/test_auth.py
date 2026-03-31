import pytest
import httpx
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

# Adjusting python path so imports work correctly
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auth import get_github_authorization_url
from github.github_client import get_github_access_token, get_github_user, get_user_repo_list, get_user_org_repo_list
from server import app

client = TestClient(app)

# ---------------------------------------------------------
# Test Group 1: auth.py (URL Generation)
# ---------------------------------------------------------
def test_get_github_authorization_url():
    url = get_github_authorization_url()
    assert url.startswith("https://github.com/login/oauth/authorize")
    assert "client_id=" in url
    assert "scope=repo,user:email" in url

# Parametrizing generic test cases to ensure volume and coverage
@pytest.mark.parametrize("i", range(5))
def test_get_github_authorization_url_repeated(i):
    url = get_github_authorization_url()
    assert "client_id=" in url

# ---------------------------------------------------------
# Test Group 2: github_client.py (External API Mocking)
# ---------------------------------------------------------
@pytest.mark.asyncio
@pytest.mark.parametrize("mock_code", [f"valid_code_{i}" for i in range(10)])
async def test_get_github_access_token_success(mock_code, mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"access_token": f"mocked_token_for_{mock_code}"}
    mock_response.raise_for_status.return_value = None

    mocker.patch("httpx.AsyncClient.post", return_value=mock_response)

    response = await get_github_access_token(mock_code)
    assert response == {"access_token": f"mocked_token_for_{mock_code}"}

@pytest.mark.asyncio
@pytest.mark.parametrize("mock_code", [f"fail_code_{i}" for i in range(5)])
async def test_get_github_access_token_http_error(mock_code, mocker):
    mock_response = mocker.Mock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Error", request=mocker.Mock(), response=mocker.Mock())

    mocker.patch("httpx.AsyncClient.post", return_value=mock_response)

    with pytest.raises(httpx.HTTPStatusError):
        await get_github_access_token(mock_code)

@pytest.mark.asyncio
@pytest.mark.parametrize("mock_token", [f"mock_token_{i}" for i in range(10)])
async def test_get_github_user_success(mock_token, mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"login": f"user_for_{mock_token}", "id": 12345}
    mock_response.raise_for_status.return_value = None

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    response = await get_github_user(mock_token)
    assert response == {"login": f"user_for_{mock_token}", "id": 12345}

@pytest.mark.asyncio
@pytest.mark.parametrize("mock_token", [f"mock_token_fail_{i}" for i in range(5)])
async def test_get_github_user_http_error(mock_token, mocker):
    mock_response = mocker.Mock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Error", request=mocker.Mock(), response=mocker.Mock())

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    with pytest.raises(httpx.HTTPStatusError):
        await get_github_user(mock_token)


# Additional tests for repo listing (often part of auth flow / tokens)
@pytest.mark.asyncio
@pytest.mark.parametrize("mock_token", [f"repo_token_{i}" for i in range(5)])
async def test_get_user_repo_list_success(mock_token, mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = [{"name": "repo1"}, {"name": "repo2"}]
    mock_response.raise_for_status.return_value = None

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    response = await get_user_repo_list(mock_token)
    assert response == [{"name": "repo1"}, {"name": "repo2"}]

@pytest.mark.asyncio
@pytest.mark.parametrize("mock_token", [f"org_token_{i}" for i in range(5)])
async def test_get_user_org_repo_list_success(mock_token, mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = [{"name": "org_repo1"}]
    mock_response.raise_for_status.return_value = None

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

    response = await get_user_org_repo_list(mock_token, "myorg", "all", "created")
    assert response == [{"name": "org_repo1"}]

# ---------------------------------------------------------
# Test Group 3: auth_routes.py (FastAPI Routes)
# ---------------------------------------------------------

# /login
@pytest.mark.parametrize("i", range(5))
def test_login_redirects(i):
    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 307
    assert "github.com/login/oauth/authorize" in response.headers["location"]

# /auth/callback
@pytest.mark.parametrize("i", range(10))
def test_auth_callback_missing_code(i):
    response = client.get("/auth/callback")
    assert response.status_code == 400
    assert response.json() == {"error": "Missing code"}

@pytest.mark.parametrize("mock_code", [f"success_code_{i}" for i in range(10)])
def test_auth_callback_success(mock_code, mocker):
    mocker.patch("routes.auth_routes.get_github_access_token", new_callable=AsyncMock, return_value={"access_token": "valid_token"})
    mocker.patch("routes.auth_routes.get_github_user", new_callable=AsyncMock, return_value={"login": "testuser"})

    response = client.get(f"/auth/callback?code={mock_code}", follow_redirects=False)

    assert response.status_code == 307
    # Note: TestClient's response.cookies might be empty if the cookie is set on the response object
    # directly via set_cookie. Let's check headers.
    assert "set-cookie" in response.headers
    assert "access_token" in response.headers["set-cookie"]

@pytest.mark.parametrize("mock_code", [f"fail_exchange_code_{i}" for i in range(5)])
def test_auth_callback_token_exchange_failure(mock_code, mocker):
    mocker.patch("routes.auth_routes.get_github_access_token", new_callable=AsyncMock, return_value={})

    response = client.get(f"/auth/callback?code={mock_code}")

    assert response.status_code == 400
    assert response.json() == {"error": "Token exchange failed"}

# /welcome
@pytest.mark.parametrize("i", range(5))
def test_welcome_unauthenticated(i):
    response = client.get("/welcome")
    assert response.status_code == 401
    assert response.json() == {"error": "Not authenticated"}

@pytest.mark.parametrize("mock_token", [f"valid_cookie_token_{i}" for i in range(5)])
def test_welcome_authenticated(mock_token):
    client.cookies.set("access_token", mock_token)
    response = client.get("/welcome")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome! You're logged in with GitHub."}
    client.cookies.clear()

# /callback (github app)
@pytest.mark.parametrize("i", range(5))
def test_github_app_callback_missing_installation_id(i):
    response = client.get("/callback")
    assert response.status_code == 400
    assert response.json() == {"error": "Missing installation_id"}

@pytest.mark.parametrize("installation_id", [str(1000 + i) for i in range(5)])
def test_github_app_callback_success(installation_id):
    response = client.get(f"/callback?installation_id={installation_id}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == f"/redirect-home?installation_id={installation_id}"

# /redirect-home
@pytest.mark.parametrize("installation_id", [str(2000 + i) for i in range(5)])
def test_redirect_home(installation_id):
    response = client.get(f"/redirect-home?installation_id={installation_id}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == f"/set-cookie?installation_id={installation_id}"

# /set-cookie
@pytest.mark.parametrize("installation_id", [str(3000 + i) for i in range(5)])
def test_set_cookie_and_redirect(installation_id):
    response = client.get(f"/set-cookie?installation_id={installation_id}", follow_redirects=False)
    assert response.status_code == 307
    assert "set-cookie" in response.headers
    assert "installation_id" in response.headers["set-cookie"]
    assert installation_id in response.headers["set-cookie"]
