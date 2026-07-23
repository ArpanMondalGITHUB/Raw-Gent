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

class AgentMessage(BaseModel):
    role: RoleType
    content: str
    timestamp: str

class WebSocketMessageType (str,Enum):
    USER_MESSAGE ="user_message"
    CREATE_PR = "create_pr"
    AGENT_MESSAGE = "agent_message"
    STATUS_UPDATE = "status_update"
    ERROR = "error"

class FileChange(BaseModel):
    file_path: str
    original_content: Optional[str] = None
    modified_content: str
    change_type: ChangeType
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

class JobUpdate(BaseModel):
    status: JobStatus
    messages: Optional[List[AgentMessage]] = None
    file_changes: Optional[List[FileChange]] = None
    pr_result: Optional[PullRequestResult] = None
    current_step: Optional[str] = None
    error: Optional[str] = None

class WebScoketMessage(BaseModel):
    type : WebSocketMessageType
    content : str
    job_id : Optional[str] = None
    timestamp : str
