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
    AGENT_MESSAGE = "agent_message"
    STATUS_UPDATE = "status_update"
    ERROR = "error"

class FileChange(BaseModel):
    file_path: str
    original_content: Optional[str] = None
    modified_content: str
    change_type: ChangeType
    language: str

class JobUpdate(BaseModel):
    status: JobStatus
    messages: Optional[List[AgentMessage]] = None
    file_changes: Optional[List[FileChange]] = None
    current_step: Optional[str] = None
    error: Optional[str] = None

class WebScoketMessage(BaseModel):
    type : WebSocketMessageType
    content : str
    job_id : Optional[str] = None
    timestamp : str