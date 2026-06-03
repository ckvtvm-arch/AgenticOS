from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime

class AgentStatus(str, Enum):
    Running = "Running"
    Paused = "Paused"
    Idle = "Idle"
    Terminated = "Terminated"

class ResourceType(str, Enum):
    CPU = "CPU"
    GPU = "GPU"
    Memory = "Memory"
    TokenBudget = "Token Budget"

class SystemServiceStatus(str, Enum):
    Online = "Online"
    Degraded = "Degraded"
    Offline = "Offline"

class Agent(BaseModel):
    id: str
    name: str
    status: AgentStatus
    resource_usage: Dict[str, float]  # {cpu: percentage, gpu: percentage, memory: percentage}
    
    class Config:
        use_enum_values = True

class Resource(BaseModel):
    type: ResourceType
    usage: float  # percentage
    total: int
    unit: str
    
    class Config:
        use_enum_values = True

class SystemService(BaseModel):
    name: str
    status: SystemServiceStatus
    
    class Config:
        use_enum_values = True