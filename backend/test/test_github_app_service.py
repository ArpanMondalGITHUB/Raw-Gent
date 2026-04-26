from unittest.mock import AsyncMock, MagicMock , patch
import pytest
from services.github_app_service import get_repo_branches, get_repos_from_installation, get_user_installation_id

	
# Type 3 (build mock_response + mock_client + patch httpx)

@pytest.mark.asyncio
async def test_get_user_installation_id_success():
	# 1. mock response
	mock_response = MagicMock()
	mock_response.status_code = 200
	mock_response.json.return_value = {
		"installations":[
			{"id":"installation_999"}
        ]
    }
	
    # 2. mock_client
	mock_client = MagicMock()
	mock_client.get = AsyncMock(return_value = mock_response)
	
	with patch("services.github_app_service.httpx.AsyncClient") as mock_class:
		mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
		mock_class.return_value.__aexit__ = AsyncMock(return_value=None)
		result = await get_user_installation_id("fake_user_token")
		
		assert result == "installation_999"
		
@pytest.mark.asyncio
async def test_get_user_installation_id_returns_none_when_no_installation():
	# 1. mock response
	mock_response = MagicMock()
	mock_response.status_code = 400
	
    # 2. mock_client
	mock_client = MagicMock()
	mock_client.get = AsyncMock(return_value = mock_response)
	
	with patch("services.github_app_service.httpx.AsyncClient") as mock_class:
		mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
		mock_class.return_value.__aexit__ = AsyncMock(return_value=None)
		result = await get_user_installation_id("fake_token")
		
		assert result is None
		
@pytest.mark.asyncio
async def test_get_user_installation_id_returns_none_when_status_not_200():
	# 1. mock response
	mock_response = MagicMock()
	mock_response.status_code = 401
	
    # 2. mock_client
	mock_client = MagicMock()
	mock_client.get = AsyncMock(return_value = mock_response)
	
	with patch("services.github_app_service.httpx.AsyncClient") as mock_class:
		mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
		mock_class.return_value.__aexit__ = AsyncMock(return_value=None)
		result = await get_user_installation_id("fake_user_token")
		
		assert result is None


@pytest.mark.asyncio
async def test_get_repos_from_installation_success():

    # mock the httpx response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "repositories": [
            {"name": "repo-one"},
            {"name": "repo-two"},
        ]
    }

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("services.github_app_service.generate_jwt",
               return_value="fake.jwt.token"), \
         patch("services.github_app_service.get_installation_access_token",
               new_callable=AsyncMock,
               return_value={"token": "fake_install_token"}), \
         patch("services.github_app_service.httpx.AsyncClient") as mock_class:
 

        mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await get_repos_from_installation("installation_999")

    assert len(result["repositories"]) == 2
    assert result["repositories"][0]["name"] == "repo-one"
    assert result["repositories"][0]["installation_id"] == "installation_999"

@pytest.mark.asyncio
async def test_get_repos_from_installation_generate_jwt_failed():
	
	with patch("services.github_app_service.generate_jwt",
           side_effect=Exception("No private key")):
		with pytest.raises(Exception):
			await get_repos_from_installation("install_999")

@pytest.mark.asyncio
async def test_get_repos_from_installation_returns_no_installation_token():
	mock_response = MagicMock()
	mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
	with patch("services.github_app_service.generate_jwt", return_value="jwt"), \
		patch("services.github_app_service.get_installation_access_token",
           new_callable=AsyncMock,
           return_value={"error": "no token here"}):
		with pytest.raises(Exception):
			await get_repos_from_installation("install_999")

@pytest.mark.asyncio
async def test_get_repos_from_installation_github_api_returns_error():
	mock_response = MagicMock()
	mock_response.raise_for_status.side_effect = Exception("500 Server Error")
	mock_client = MagicMock()
	mock_client.get = AsyncMock(return_value=mock_response)

	with patch("services.github_app_service.generate_jwt", return_value="jwt"), \
		patch("services.github_app_service.get_installation_access_token",
		new_callable=AsyncMock,
		return_value={"token": "fake_token"}), \
			patch("services.github_app_service.httpx.AsyncClient") as mock_class:
		
		mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
		mock_class.return_value.__aexit__ = AsyncMock(return_value=None)
		with pytest.raises(Exception):
			await get_repos_from_installation("install_999")

@pytest.mark.asyncio
async def test_get_repos_from_installation_return_empty_reposotories_list():
	mock_response = MagicMock()
	mock_response.raise_for_status.return_value = None
	mock_response.json.return_value = {"repositories": []}

	mock_client = MagicMock()
	mock_client.get = AsyncMock(return_value=mock_response)

	with patch("services.github_app_service.generate_jwt", return_value="jwt"), \
		patch("services.github_app_service.get_installation_access_token",
		new_callable=AsyncMock,
		return_value={"token": "fake_token"}), \
			patch("services.github_app_service.httpx.AsyncClient") as mock_class:
		
		mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
		mock_class.return_value.__aexit__ = AsyncMock(return_value=None)
		
		result = await get_repos_from_installation("install_999")

		assert result["repositories"] == []

# ----------------------------------GET-REPO-BRANCHES-------------------------------------------

@pytest.mark.asyncio
async def test_get_repo_branches_generate_jwt_failed():
    with patch("services.github_app_service.generate_jwt",
               side_effect=Exception("No private key")):
        with pytest.raises(Exception):
            await get_repo_branches("install_999", "repo-one")

@pytest.mark.asyncio
async def test_get_repo_branches_get_installation_access_token_failed():
	mock_response = MagicMock()
	mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
	with patch("services.github_app_service.generate_jwt",
			 return_value="jwt"), \
		patch("services.github_app_service.get_installation_access_token",
           new_callable=AsyncMock,
           side_effect=Exception("Token failed")):
		with pytest.raises(Exception):
			await get_repo_branches("install_999", "repo-one")

@pytest.mark.asyncio
async def test_get_repo_branches_github_api_returns_error():
	mock_response = MagicMock()
	mock_response.raise_for_status.side_effect = Exception("500 Server Error")
	mock_client = MagicMock()
	mock_client.get = AsyncMock(return_value=mock_response)

	with patch("services.github_app_service.generate_jwt", return_value="jwt"), \
		patch("services.github_app_service.get_installation_access_token",
		new_callable=AsyncMock,
		return_value={"token": "fake_token"}), \
			patch("services.github_app_service.httpx.AsyncClient") as mock_class:
		
		mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
		mock_class.return_value.__aexit__ = AsyncMock(return_value=None)
		with pytest.raises(Exception):
			await get_repos_from_installation("install_999")

@pytest.mark.asyncio
async def test_get_repo_branches_target_repo_not_found():
    # your code: if not target_repo: raise Exception("Repository not found")
    # simulate GitHub returning repos but none match the requested repo_name

    mock_repos_response = MagicMock()
    mock_repos_response.raise_for_status.return_value = None
    mock_repos_response.json.return_value = {
        "repositories": [
            {"name": "different-repo", "owner": {"login": "arpan"}}
            # ↑ no repo called "repo-one" → target_repo stays None → exception
        ]
    }

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_repos_response)

    with patch("services.github_app_service.generate_jwt", return_value="jwt"), \
         patch("services.github_app_service.get_installation_access_token",
               new_callable=AsyncMock,
               return_value={"token": "fake_token"}), \
         patch("services.github_app_service.httpx.AsyncClient") as mock_class:

        mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

        with pytest.raises(Exception) as exc_info:
            await get_repo_branches("install_999", "repo-one")

        assert "repo-one" in str(exc_info.value)
        assert "not found" in str(exc_info.value)
        # ↑ your code raises: f"Repository '{repo_name}' not found in installation"


@pytest.mark.asyncio
async def test_get_repo_branches_success():
    # this function makes TWO client.get calls:
    # call 1 → get all repos to find the owner
    # call 2 → get branches for that repo
    # use side_effect with a list to return different responses each call

    mock_repos_response = MagicMock()
    mock_repos_response.raise_for_status.return_value = None
    mock_repos_response.json.return_value = {
        "repositories": [
            {"name": "repo-one", "owner": {"login": "arpan"}}
        ]
    }

    mock_branches_response = MagicMock()
    mock_branches_response.raise_for_status.return_value = None
    mock_branches_response.json.return_value = [
        {"name": "main"},
        {"name": "dev"}
    ]

    mock_client = MagicMock()
    mock_client.get = AsyncMock(side_effect=[mock_repos_response, mock_branches_response])
    # ↑ side_effect with a LIST means:
    # first call to client.get() → returns mock_repos_response
    # second call to client.get() → returns mock_branches_response

    with patch("services.github_app_service.generate_jwt", return_value="jwt"), \
         patch("services.github_app_service.get_installation_access_token",
               new_callable=AsyncMock,
               return_value={"token": "fake_token"}), \
         patch("services.github_app_service.httpx.AsyncClient") as mock_class:

        mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await get_repo_branches("install_999", "repo-one")

    assert len(result) == 2
    assert result[0]["name"] == "main"
    assert result[1]["name"] == "dev"
