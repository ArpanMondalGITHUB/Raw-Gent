from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ChangeType(str, Enum):
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"

class RoleType(str, Enum):
    USER = "user"
    AGENT = "agent"

class RunAgentRequest(BaseModel):
    prompt:str
    repo_name:str
    installation_id: int
    branches: str

class RunAgentResponse(BaseModel):
    job_id:str
    status: str = "queued"

class FileChange(BaseModel):
    file_path: str
    original_content: Optional[str] = None
    modified_content: str
    change_type: ChangeType  # "created", "modified", "deleted"
    language: str

class PullRequestResult(BaseModel):
    branch_name: str
    branch_url: str
    pr_url: str
    pr_number: int
    title: str
    body: Optional[str] = None
    additions: int = 0
    deletions: int = 0

class AgentMessage(BaseModel):
    role: RoleType  # "agent" or "user"
    content: str
    timestamp: str

class JobStatusResponse(BaseModel):
    """Complete job status - stored in backend and returned to frontend"""
    job_id: str
    status: JobStatus
    messages: List[AgentMessage]
    file_changes: List[FileChange]
    pr_result: Optional[PullRequestResult] = None
    current_step: Optional[str] = None
    error: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
