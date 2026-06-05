from pydantic import BaseModel
from typing import Dict, List, Optional
from .models import AgentStatus, ResourceType, SystemServiceStatus

# Agent schemas
class AgentCreate(BaseModel):
    name: str
    script_name: Optional[str] = None
    priority: Optional[int] = 50
    capabilities: Optional[List[str]] = None
    metadata: Optional[Dict[str, str]] = None

class AgentUpdate(BaseModel):
    status: AgentStatus

class AgentResponse(BaseModel):
    id: str
    name: str
    status: AgentStatus
    script_name: str
    pid: Optional[int]
    priority: int
    capabilities: List[str]
    metadata: Dict[str, str]
    created_at: Optional[str]
    started_at: Optional[str]
    terminated_at: Optional[str]
    heartbeat_at: Optional[str]
    cpu_percent: float
    memory_mb: float

# Resource schemas
class ResourceResponse(BaseModel):
    type: ResourceType
    usage: float
    total: int
    unit: str

# System Service schemas
class SystemServiceResponse(BaseModel):
    name: str
    status: SystemServiceStatus