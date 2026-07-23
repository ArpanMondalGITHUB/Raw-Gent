"""MCP client for the GitHub MCP server.

Replaces the hand-written GitHub REST calls in services/github_app_service.py
(and eventually the PR-creation call in job_runner/main.py) with tool calls
to GitHub's hosted MCP server.

Auth model in this project: GitHub App -> short-lived installation access
token (minted by services.github_app_service.mint_installation_token). That
token rides in the Authorization header of the MCP connection, so one
GitHubMCP instance == one installation's identity. Never share an instance
across installations/users.

Quick probe (verifies the token works against the hosted server):

    cd backend
    poetry run python -m mcp_clients.github_mcp <installation_id>
"""

import json
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from github.github_app_client import _load_private_key

GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"


class GitHubMCP:
    """A per-token MCP session to GitHub's hosted MCP server.

    Usage:
        async with await GitHubMCP.for_installation(installation_id) as gh:
            branches = await gh.list_branches("owner", "repo")
    """

    def __init__(self, token: str):
        self._token = token
        self._stack = AsyncExitStack()
        self.session: ClientSession | None = None

    @classmethod
    async def for_installation(cls, installation_id: str) -> "GitHubMCP":
        # Imported here so mcp_clients stays decoupled from services at import time
        from services.github_app_service import mint_installation_token

        token = await mint_installation_token(installation_id)
        return cls(token)
    private_key = _load_private_key()
    async def __aenter__(self) -> "GitHubMCP":
        read, write, _ = await self._stack.enter_async_context(
            streamablehttp_client(
                GITHUB_MCP_URL,
                headers={"Authorization": f"Bearer {self._token}"},
            )
        )
        self.session = await self._stack.enter_async_context(
            ClientSession(read, write)
        )
        await self.session.initialize()
        return self

    async def __aexit__(self, *exc):
        await self._stack.aclose()

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    async def _call(self, tool: str, args: dict) -> str:
        """Direct (no-LLM) tool call. Returns concatenated text content."""
        result = await self.session.call_tool(tool, args)
        text = "\n".join(c.text for c in result.content if c.type == "text")
        if result.isError:
            raise RuntimeError(f"MCP tool '{tool}' failed: {text}")
        return text

    async def _call_json(self, tool: str, args: dict):
        return json.loads(await self._call(tool, args))

    async def tool_names(self) -> list[str]:
        """Debug helper: what tools does the server expose to this token?"""
        result = await self.session.list_tools()
        return [t.name for t in result.tools]

    # ------------------------------------------------------------------
    # replacements for the REST helpers
    # ------------------------------------------------------------------

    async def list_branches(self, owner: str, repo: str) -> list[dict]:
        """Replaces services.github_app_service.get_repo_branches (REST).

        Note: unlike the REST helper, this takes owner directly instead of
        scanning installation repositories to find it.
        """
        data = self._as_list(
            await self._call_json("list_branches", {"owner": owner, "repo": repo})
        )
        return data

    async def search_repositories(self, query: str, per_page: int = 50) -> list[dict]:
        """e.g. query='org:my-org' or 'user:someone'."""
        data = await self._call_json(
            "search_repositories", {"query": query, "perPage": per_page}
        )
        return data.get("items", data) if isinstance(data, dict) else data

    async def get_file_contents(self, owner: str, repo: str, path: str,
                                ref: str | None = None) -> str:
        args = {"owner": owner, "repo": repo, "path": path}
        if ref:
            args["ref"] = ref
        return await self._call("get_file_contents", args)

    async def create_branch(self, owner: str, repo: str,
                            branch: str, from_branch: str) -> None:
        await self._call("create_branch", {
            "owner": owner, "repo": repo,
            "branch": branch, "from_branch": from_branch,
        })

    async def create_pull_request(self, owner: str, repo: str, title: str,
                                  body: str, head: str, base: str) -> str:
        """Replaces the raw POST /repos/{owner}/{repo}/pulls call
        (job_runner/main.py). Returns the PR URL."""
        data = await self._call_json("create_pull_request", {
            "owner": owner, "repo": repo,
            "title": title, "body": body,
            "head": head, "base": base,
        })
        return data.get("html_url", str(data)) if isinstance(data, dict) else str(data)

    @staticmethod
    def _as_list(data) -> list:
        """The server returns JSON; normalize dict-wrapped lists."""
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("branches", "items", "data"):
                if isinstance(data.get(key), list):
                    return data[key]
        return [data]


# ----------------------------------------------------------------------
# Probe: poetry run python -m mcp_clients.github_mcp <installation_id>
# Verifies (1) connectivity, (2) that an installation token is accepted
# by the hosted server, (3) the current tool names to code against.
# ----------------------------------------------------------------------

async def _probe(installation_id: str) -> None:
    gh = await GitHubMCP.for_installation(installation_id)
    async with gh:
        names = await gh.tool_names()
        print(f"Connected. {len(names)} tools available. First 20:")
        for n in names[:20]:
            print(f"  - {n}")


if __name__ == "__main__":
    import asyncio
    import sys

    if len(sys.argv) != 2:
        sys.exit("usage: python -m mcp_clients.github_mcp <installation_id>")
    asyncio.run(_probe(sys.argv[1]))
