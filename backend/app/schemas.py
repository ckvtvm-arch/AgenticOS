from pydantic import BaseModel
from typing import Dict, Optional
from .models import AgentStatus, ResourceType, SystemServiceStatus

# Agent schemas
class AgentCreate(BaseModel):
    name: str

class AgentUpdate(BaseModel):
    status: AgentStatus

class AgentResponse(BaseModel):
    id: str
    name: str
    status: AgentStatus
    resource_usage: Dict[str, float]

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