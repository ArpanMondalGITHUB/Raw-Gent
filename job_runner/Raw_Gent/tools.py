"""
File operation tools for ADK agents.
These tools allow agents to read, write, and list files in the cloned repository.
"""
import logging
import os
from typing import Any
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)


def _resolve_repo_path(context: Any = None) -> str | None:
    """Resolve the cloned repo path from ADK session state or environment."""
    if context is not None:
        try:
            invocation_context = getattr(context, "_invocation_context", None)
            session = getattr(invocation_context, "session", None)
            state = getattr(session, "state", None)
            if isinstance(state, dict):
                repo_path = state.get("repo_path")
                if repo_path:
                    return str(repo_path)
        except (AttributeError, TypeError, KeyError) as exc:
            logger.debug("Unable to resolve repo_path from invocation_context/session/state: %s", exc, exc_info=True)

        try:
            session = getattr(context, "session", None)
            state = getattr(session, "state", None)
            if isinstance(state, dict):
                repo_path = state.get("repo_path")
                if repo_path:
                    return str(repo_path)
        except (AttributeError, TypeError, KeyError) as exc:
            logger.debug("Unable to resolve repo_path from context.session/state: %s", exc, exc_info=True)

        try:
            state = context.get("state") if isinstance(context, dict) else None
            if isinstance(state, dict):
                repo_path = state.get("repo_path")
                if repo_path:
                    return str(repo_path)
        except (AttributeError, TypeError, KeyError) as exc:
            logger.debug("Unable to resolve repo_path from context['state']: %s", exc, exc_info=True)

    repo_path = os.getenv("REPO_PATH")
    return repo_path.strip() if repo_path and repo_path.strip() else None


def _resolve_full_path(relative_path: str, context: Any = None) -> tuple[str | None, str | None]:
    repo_path = _resolve_repo_path(context)
    if not repo_path:
        return None, "Error: Repository path not available. Check ADK session state or REPO_PATH."

    repo_path_abs = os.path.normcase(os.path.realpath(repo_path))
    full_path = os.path.normcase(os.path.realpath(os.path.join(repo_path_abs, relative_path)))

    try:
        if os.path.commonpath([repo_path_abs, full_path]) != repo_path_abs:
            return None, "Error: Invalid path - cannot access files outside repository"
    except ValueError:
        return None, "Error: Invalid path - cannot access files outside repository"

    return full_path, None


def read_file_from_repo(relative_path: str, tool_context: ToolContext) -> str:
    """
    Read a file from the cloned repository.
    """
    try:
        full_path, error = _resolve_full_path(relative_path, tool_context)
        if error:
            return error

        with open(full_path, "r", encoding="utf-8", errors="ignore") as file_handle:
            content = file_handle.read()

        return f"File: {relative_path}\n\n{content}"
    except FileNotFoundError:
        return f"Error: File '{relative_path}' not found in repository"
    except IsADirectoryError:
        return f"Error: '{relative_path}' is a directory, not a file"
    except Exception as exc:
        return f"Error reading file '{relative_path}': {exc}"


def write_file_to_repo(relative_path: str, content: str, tool_context: ToolContext) -> str:
    """
    Write content to a file in the cloned repository.
    """
    try:
        full_path, error = _resolve_full_path(relative_path, tool_context)
        if error:
            return error.replace("access files", "write files")

        parent_dir = os.path.dirname(full_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as file_handle:
            file_handle.write(content)

        return f"Successfully wrote {len(content)} characters to {relative_path}"
    except Exception as exc:
        return f"Error writing file '{relative_path}': {exc}"


def list_files_in_repo(tool_context: ToolContext, directory: str = ".") -> str:
    """
    List files and directories under a repository path.
    """
    try:
        full_path, error = _resolve_full_path(directory, tool_context)
        if error:
            return error.replace("files", "directories")

        if not os.path.isdir(full_path):
            return f"Error: '{directory}' is not a directory"

        items = sorted(os.listdir(full_path))
        result = [f"Contents of '{directory}':"]
        for item in items:
            item_path = os.path.join(full_path, item)
            prefix = "📁" if os.path.isdir(item_path) else "📄"
            suffix = "/" if os.path.isdir(item_path) else ""
            result.append(f"{prefix} {item}{suffix}")

        return "\n".join(result)
    except Exception as exc:
        return f"Error listing files in '{directory}': {exc}"
