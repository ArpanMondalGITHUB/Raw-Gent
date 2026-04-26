import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from github.github_app_client import (
    generate_jwt,
    get_installation_access_token,
)

class DummyResponse:
	def __init__(self, data=None, exc=None):
		self._data = data or {}
		self._exc = exc

	def raise_for_status(self):
		if self._exc:
			raise self._exc

	def json(self):
		return self._data
      
class AsyncClientMock:
	def __init__(self, response: DummyResponse):
		self._response = response
		self.last_call = None

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc, tb):
		return False

	async def post(self, url, json=None, headers=None):
		self.last_call = ("post", url, json, headers)
		return self._response

	async def get(self, url, headers=None, params=None):
		self.last_call = ("get", url, headers, params)
		return self._response

def test_generate_jwt_returns_a_string():
    with patch("github.github_app_client.pyjwt.encode") as mock_encode, \
         patch("github.github_app_client.GITHUB_APP_CLIENT_ID", "fake_app_id"), \
         patch("github.github_app_client.GITHUB_PRIVATE_KEY", "fake-key-string"):


        mock_encode.return_value = "fake.jwt.token"

        result = generate_jwt()

    assert isinstance(result, str)
    assert result == "fake.jwt.token"

def test_generate_jwt_sends_correct_payload():
    with patch("github.github_app_client.pyjwt.encode") as mock_encode, \
         patch("github.github_app_client.GITHUB_APP_CLIENT_ID", "fake_app_id"), \
         patch("github.github_app_client.GITHUB_PRIVATE_KEY", "fake-key-string"):
        
        mock_encode.return_value = "fake.jwt.token"

        generate_jwt()

        call_args = mock_encode.call_args.args

        payload = call_args[0]

        assert "iat" in payload
        assert "exp" in payload
        assert payload["exp"] == payload["iat"] + 600
        assert payload["iss"] == "fake_app_id"

def test_generate_jwt_using_RS256_algorithm():
        with patch("github.github_app_client.pyjwt.encode") as mock_encode, \
         patch("github.github_app_client.GITHUB_APP_CLIENT_ID", "fake_app_id"), \
         patch("github.github_app_client.GITHUB_PRIVATE_KEY", "fake-key-string"):
             
             mock_encode.return_value = "fake.jwt.token"

             generate_jwt()

             call_kwargs = mock_encode.call_args.kwargs

             assert call_kwargs["algorithm"] == "RS256"


@pytest.mark.asyncio
async def test_get_installation_access_token_returns_token():
    # This function takes jwt_token and installation_id as arguments
    # so NO config patching needed — we just pass them directly

    # Step 1 - fake response
    mock_response = MagicMock()
    mock_response.json.return_value = {"token": "fake_install_token_abc"}
    mock_response.raise_for_status.return_value = None

    # Step 2 - fake client
    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    # ↑ post not get — your function uses client.post()

    # Step 3 - patch httpx
    with patch("github.github_app_client.httpx.AsyncClient") as mock_class:
        mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await get_installation_access_token("fake_jwt_token", "installation_999")
        #                                             ↑ just pass values directly
        #                                             no patching needed because
        #                                             they are function ARGUMENTS
        #                                             not config variables

    assert result == {"token": "fake_install_token_abc"}


@pytest.mark.asyncio
async def test_get_installation_access_token_builds_correct_url():

    mock_response = MagicMock()
    mock_response.json.return_value = {"token": "abc"}
    mock_response.raise_for_status.return_value = None

    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch("github.github_app_client.httpx.AsyncClient") as mock_class:
        mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

        await get_installation_access_token("my_jwt", "install_id_555")

    # check the URL that post() was called with
    call_args = mock_client.post.call_args.args
    assert "install_id_555" in call_args[0]
    # ↑ your code builds: f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    # so installation_id must appear in the URL


@pytest.mark.asyncio
async def test_get_installation_access_token_sends_correct_headers():

    mock_response = MagicMock()
    mock_response.json.return_value = {"token": "abc"}
    mock_response.raise_for_status.return_value = None

    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch("github.github_app_client.httpx.AsyncClient") as mock_class:
        mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

        await get_installation_access_token("my_jwt_token_123", "install_999")

    call_kwargs = mock_client.post.call_args.kwargs
    # ↑ get keyword arguments: headers=...

    assert call_kwargs["headers"]["Authorization"] == "Bearer my_jwt_token_123"
    # ↑ your code: f"Bearer {jwt_token}" — verify token was inserted correctly
    assert call_kwargs["headers"]["Accept"] == "application/vnd.github+json"
