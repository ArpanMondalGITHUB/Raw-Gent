from typing import Any, Dict
from pydantic import BaseModel


class AgentRunRequest(BaseModel):
    prompt: str
    repo_name: str  
    installation_id: int
    branches: str

class AgentResponse(BaseModel):
    success: bool
    result: Dict[Any, Any]
    message: str