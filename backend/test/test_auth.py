from auth import get_github_authorization_url
from unittest.mock import patch

# ─── Test 1: Basic URL structure ────────────────────────────────────────────

def test_get_github_authorization_url():
    url = get_github_authorization_url()

    assert "https://github.com/login/oauth/authorize" in url

# ─── Test 2: client_id is in the URL ────────────────────────────────────────

def test_get_github_authorzation_url_has_cliet_id():
    with patch ("auth.GITHUB_CLIENT_ID" , "fake_client_id_1234"):
        url = get_github_authorization_url()

        assert "client_id=" in url

# ─── Test 3: scope is always included ───────────────────────────────────────

def test_get_github_authorization_url_has_correct_scope():
    with patch("auth.GITHUB_CLIENT_ID","fake_123"):
        url = get_github_authorization_url()

        assert "scope=" in url

# ─── Test 4: redirect_uri only appears when GITHUB_CALLBACK_URL is set ──────

def test_redirect_uri_included_when_callback_url_set():
    with patch ("auth.GITHUB_CLIENT_ID","fake_123"), \
        patch ("auth.GITHUB_CALLBACK_URL","https://myapp.com/callback"):

        url = get_github_authorization_url()

        assert "redirect_uri=" in url

def test_redirect_uri_included_when_callback_url_not_set():
    with patch ("auth.GITHUB_CLIENT_ID","fake_123"), \
        patch ("auth.GITHUB_CALLBACK_URL",None):

        url = get_github_authorization_url()

        assert "redirect_uri=" not in url

