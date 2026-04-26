import pytest
from unittest.mock import patch, MagicMock
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
    # ↑ this creates a fake browser that talks to your FastAPI app


@pytest.mark.asyncio
async def test_login_redirects(client):
    # ↑ "client" here is the fixture above, not any import
    with patch("auth.get_github_authorization_url",
               return_value="https://github.com/login/oauth/authorize?client_id=fake"):

        response = await client.get("/login", follow_redirects=False)

    assert response.status_code == 307
    assert "github.com/login/oauth/authorize" in response.headers["location"]


@pytest.mark.asyncio
async def test_auth_callback_missing_code(client):
    # no ?code= in the URL → should return 400
    response = await client.get("/auth/callback")
    # ↑ no query param at all

    assert response.status_code == 400
    assert response.json() == {"error": "Missing code"}
    # ↑ your code returns this exact dict when code is missing


@pytest.mark.asyncio
async def test_auth_callback_token_exchange_failed(client):
    # GitHub returns a response but with no access_token inside
    # this tests the second if block:
    # if not access_token: return JSONResponse({"error":"Token exchange failed"})

    with patch("routes.auth_routes.get_github_access_token",
               return_value={"error": "bad_verification_code"}):
               # ↑ GitHub sometimes returns an error dict instead of access_token
               # so access_token = token_data.get("access_token") → None

        response = await client.get("/auth/callback?code=bad_code")

    assert response.status_code == 400
    assert response.json() == {"error": "Token exchange failed"}


@pytest.mark.asyncio
async def test_auth_callback_success_redirects(client):
    # happy path — valid code → get token → get user → redirect

    with patch("routes.auth_routes.get_github_access_token",
               return_value={"access_token": "valid_token_abc"}), \
         patch("routes.auth_routes.get_github_user",
               return_value={"login": "arpan", "id": 123}):
        # ↑ mock both GitHub calls
        # get_github_access_token returns a valid token
        # get_github_user returns a fake user profile

        response = await client.get(
            "/auth/callback?code=valid_code_123",
            follow_redirects=False
            # ↑ don't follow the redirect — just capture it
        )

    assert response.status_code == 307
    # ↑ should redirect to frontend home


@pytest.mark.asyncio
async def test_auth_callback_success_sets_cookie(client):
    # check that the access_token cookie is set after success

    with patch("routes.auth_routes.get_github_access_token",
               return_value={"access_token": "valid_token_abc"}), \
         patch("routes.auth_routes.get_github_user",
               return_value={"login": "arpan", "id": 123}):

        response = await client.get(
            "/auth/callback?code=valid_code_123",
            follow_redirects=False
        )

    # check the cookie was set on the response
    assert "access_token" in response.cookies
    # ↑ change "access_token" to whatever your COOKIE_ACCESS_NAME value is


@pytest.mark.asyncio
async def test_auth_callback_cookie_has_correct_value(client):
    # check the cookie value is the actual access token, not something random

    with patch("routes.auth_routes.get_github_access_token",
               return_value={"access_token": "valid_token_abc"}), \
         patch("routes.auth_routes.get_github_user",
               return_value={"login": "arpan", "id": 123}):

        response = await client.get(
            "/auth/callback?code=valid_code_123",
            follow_redirects=False
        )

    assert response.cookies["access_token"] == "valid_token_abc"
    # ↑ verify the token value in the cookie matches what GitHub returned


@pytest.mark.asyncio
async def test_welcome_missing_token(client):
    response = await client.get("/welcome")

    assert response.status_code == 401
    assert response.json() == {"error": "Not authenticated"}


@pytest.mark.asyncio
async def test_welcome_success(client):
    response = await client.get(
        "/welcome",
        cookies={"access_token": "some_fake_token"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome! You're logged in with GitHub."}


@pytest.mark.asyncio
async def test_callback_missing_installation_id(client):
    response = await client.get("/callback")

    assert response.status_code == 400
    assert response.json() == {"error": "Missing installation_id"}


@pytest.mark.asyncio
async def test_callback_success(client):
    response = await client.get(
        "/callback",
        params = {"installation_id":"fake_id_123"}
    )

    assert response.status_code == 307
    assert "installation_id=fake_id_123" in response.headers["location"]


@pytest.mark.asyncio
async def test_redirect_home_success(client):
    response = await client.get(
        "/redirect-home",
        params = {"installation_id":"fake_id_123"}
    )
    assert response.status_code == 307
    assert "installation_id=fake_id_123" in response.headers["location"]


@pytest.mark.asyncio
async def test_redirect_home_missing_installation_id(client):
    response = await client.get("/redirect-home")

    assert response.status_code == 307
    assert "installation_id=None" in response.headers["location"]


@pytest.mark.asyncio
async def test_set_cookie_redirects(client):
    response = await client.get(
        "/set-cookie",
        params={"installation_id": "fake_id_123"},
        follow_redirects=False
    )

    assert response.status_code == 307


@pytest.mark.asyncio
async def test_set_cookie_sets_correct_cookie(client):
    response = await client.get(
        "/set-cookie",
        params={"installation_id": "fake_id_123"},
        follow_redirects=False
    )

    assert "installation_id" in response.cookies
    assert response.cookies["installation_id"] == "fake_id_123"

