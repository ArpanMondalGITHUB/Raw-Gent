import pytest
import httpx

from github.github_client import (
	get_github_access_token,
	get_github_user,
	get_user_repo_list,
	get_user_org_repo_list,
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


@pytest.mark.asyncio
async def test_get_github_access_token_success(monkeypatch):
	resp = DummyResponse({"access_token": "tok123"})
	mock_client = AsyncClientMock(resp)
	monkeypatch.setattr(httpx, "AsyncClient", lambda *a, **k: mock_client)

	result = await get_github_access_token("code-xyz")
	assert result == {"access_token": "tok123"}

	assert mock_client.last_call is not None
	method, url, payload, headers = mock_client.last_call
	assert method == "post"
	assert url == "https://github.com/login/oauth/access_token"
	assert headers == {"Accept": "application/json"}
	assert payload["code"] == "code-xyz"


@pytest.mark.asyncio
async def test_get_github_access_token_raises_on_http_error(monkeypatch):
	resp = DummyResponse(None, exc=Exception("status error"))
	mock_client = AsyncClientMock(resp)
	monkeypatch.setattr(httpx, "AsyncClient", lambda *a, **k: mock_client)

	with pytest.raises(Exception):
		await get_github_access_token("bad-code")


@pytest.mark.asyncio
async def test_get_github_user_success_and_auth_header(monkeypatch):
	resp = DummyResponse({"login": "me"})
	mock_client = AsyncClientMock(resp)
	monkeypatch.setattr(httpx, "AsyncClient", lambda *a, **k: mock_client)

	result = await get_github_user("tok-1")
	assert result == {"login": "me"}

	method, url, headers, params = mock_client.last_call
	assert method == "get"
	assert url == "https://api.github.com/user"
	assert headers.get("Authorization") == "Bearer tok-1"


@pytest.mark.asyncio
async def test_get_user_repo_list_headers_and_url(monkeypatch):
	repos = [{"name": "r1"}, {"name": "r2"}]
	resp = DummyResponse(repos)
	mock_client = AsyncClientMock(resp)
	monkeypatch.setattr(httpx, "AsyncClient", lambda *a, **k: mock_client)

	result = await get_user_repo_list("tok-2")
	assert result == repos

	method, url, headers, params = mock_client.last_call
	assert method == "get"
	assert url == "https://api.github.com/user/repos"
	assert headers["Accept"] == "application/vnd.github+json"
	assert headers["Authorization"] == "Bearer tok-2"


@pytest.mark.asyncio
async def test_get_user_org_repo_list_params_and_headers(monkeypatch):
	resp = DummyResponse([{"repo": "x"}])
	mock_client = AsyncClientMock(resp)
	monkeypatch.setattr(httpx, "AsyncClient", lambda *a, **k: mock_client)

	result = await get_user_org_repo_list("tok-3", "myorg", "public", "created")
	assert result == [{"repo": "x"}]

	method, url, headers, params = mock_client.last_call
	assert method == "get"
	assert url == "https://api.github.com/orgs/myorg/repos"
	assert params == {"type": "public", "sort": "created"}
	assert headers["X-GitHub-Api-Version"] == "2022-11-28"
	assert headers["Accept"] == "application/vnd.github+json"
