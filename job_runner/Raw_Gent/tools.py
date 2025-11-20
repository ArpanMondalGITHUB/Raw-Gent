"""
File operation tools for ADK agents.
These tools allow agents to read, write, and list files in the cloned repository.
"""
import os
from typing import Optional


def read_file_from_repo(relative_path: str, context) -> str:
    """
    Reads a file from the cloned repository.

    Args:
        relative_path (str): Path to file relative to repo root (e.g., "src/main.py" or "README.md").
        
    Returns:
        str: The file contents, or an error message if the file cannot be read.
    """
    try:
        repo_path = context.session.state.get('repo_path')
        if not repo_path:
            return "Error: Repository path not found in session state. Please ensure repo_path is set."
        
        full_path = os.path.join(repo_path, relative_path)
        
        # Security check: ensure path is within repo directory
        full_path = os.path.abspath(full_path)
        repo_path_abs = os.path.abspath(repo_path)
        if not full_path.startswith(repo_path_abs):
            return f"Error: Invalid path - cannot access files outside repository"
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"File: {relative_path}\n\n{content}"
    except FileNotFoundError:
        return f"Error: File '{relative_path}' not found in repository"
    except Exception as e:
        return f"Error reading file '{relative_path}': {str(e)}"


def write_file_to_repo(relative_path: str, content: str, context) -> str:
    """
    Writes content to a file in the cloned repository.

    Args:
        relative_path (str): Path to file relative to repo root (e.g., "src/main.py").
        content (str): Content to write to the file.
        
    Returns:
        str: Success message or error message.
    """
    try:
        repo_path = context.session.state.get('repo_path')
        if not repo_path:
            return "Error: Repository path not found in session state. Please ensure repo_path is set."
        
        full_path = os.path.join(repo_path, relative_path)
        
        # Security check: ensure path is within repo directory
        full_path = os.path.abspath(full_path)
        repo_path_abs = os.path.abspath(repo_path)
        if not full_path.startswith(repo_path_abs):
            return f"Error: Invalid path - cannot write files outside repository"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {relative_path}"
    except Exception as e:
        return f"Error writing file '{relative_path}': {str(e)}"


def list_files_in_repo(directory: str = ".", context=None) -> str:
    """
    Lists files and directories in a directory of the cloned repository.

    Args:
        directory (str, optional): Directory path relative to repo root. Defaults to "." (root).
        
    Returns:
        str: Newline-separated list of files and directories, or an error message.
    """
    try:
        # ADK automatically injects context as the last parameter
        # Handle case where context might be passed positionally
        if context is None:
            return "Error: Context not available. Repository path not accessible."
        
        repo_path = context.session.state.get('repo_path')
        if not repo_path:
            return "Error: Repository path not found in session state. Please ensure repo_path is set."
        
        full_path = os.path.join(repo_path, directory)
        
        # Security check: ensure path is within repo directory
        full_path = os.path.abspath(full_path)
        repo_path_abs = os.path.abspath(repo_path)
        if not full_path.startswith(repo_path_abs):
            return f"Error: Invalid path - cannot access directories outside repository"
        
        if not os.path.isdir(full_path):
            return f"Error: '{directory}' is not a directory"
        
        items = os.listdir(full_path)
        items_sorted = sorted(items)
        
        # Format output nicely
        result = f"Contents of '{directory}':\n"
        for item in items_sorted:
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                result += f"📁 {item}/\n"
            else:
                result += f"📄 {item}\n"
        
        return result
    except Exception as e:
        return f"Error listing files in '{directory}': {str(e)}"

