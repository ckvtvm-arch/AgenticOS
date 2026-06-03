from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional
import random

from .database import init_db, get_db
from .models import Agent, Resource, SystemService, AgentStatus, ResourceType, SystemServiceStatus
from .schemas import AgentCreate, AgentUpdate, AgentResponse, ResourceResponse, SystemServiceResponse

# Global state for simulation (in production, this would come from the database/agent runtime)
agents_db: Dict[str, Agent] = {}
resources_db: List[Resource] = []
services_db: List[SystemService] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    await init_db()
    
    # Initialize mock data
    await initialize_mock_data()
    
    # Start background tasks
    asyncio.create_task(update_resources_periodically())
    asyncio.create_task(update_agents_periodically())
    
    yield
    
    # Cleanup
    # (Any cleanup code would go here)

app = FastAPI(
    title="AgenticOS Backend API",
    description="Backend API for AgenticOS Dashboard",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections
active_connections: List[WebSocket] = []

async def initialize_mock_data():
    """Initialize mock data for demonstration"""
    global agents_db, resources_db, services_db
    
    # Initialize agents
    agents_db = {
        "agent-001": Agent(
            id="agent-001",
            name="CodeOptimizer",
            status=AgentStatus.Running,
            resource_usage={"cpu": 25, "gpu": 60, "memory": 30}
        ),
        "agent-002": Agent(
            id="agent-002",
            name="DataAnalyzer",
            status=AgentStatus.Running,
            resource_usage={"cpu": 45, "gpu": 75, "memory": 50}
        ),
        "agent-003": Agent(
            id="agent-003",
            name="SystemMonitor",
            status=AgentStatus.Idle,
            resource_usage={"cpu": 5, "gpu": 2, "memory": 10}
        ),
        "agent-004": Agent(
            id="agent-004",
            name="UITaskAutomator",
            status=AgentStatus.Paused,
            resource_usage={"cpu": 10, "gpu": 5, "memory": 15}
        ),
        "agent-005": Agent(
            id="agent-005",
            name="ResearchAggregator",
            status=AgentStatus.Terminated,
            resource_usage={"cpu": 0, "gpu": 0, "memory": 0}
        ),
    }
    
    # Initialize resources
    resources_db = [
        Resource(type=ResourceType.CPU, usage=45, total=16, unit="Cores"),
        Resource(type=ResourceType.GPU, usage=78, total=24, unit="GB VRAM"),
        Resource(type=ResourceType.Memory, usage=62, total=64, unit="GB RAM"),
        Resource(type=ResourceType.TokenBudget, usage=85, total=1000000, unit="Tokens/hr"),
    ]
    
    # Initialize system services
    services_db = [
        SystemService(name="Agent Registry", status=SystemServiceStatus.Online),
        SystemService(name="Inference Engine", status=SystemServiceStatus.Online),
        SystemService(name="Context Management", status=SystemServiceStatus.Degraded),
        SystemService(name="Tool Execution", status=SystemServiceStatus.Online),
        SystemService(name="Communication Bus", status=SystemServiceStatus.Offline),
    ]

async def update_resources_periodically():
    """Simulate resource fluctuation"""
    global resources_db
    while True:
        await asyncio.sleep(2)
        for resource in resources_db:
            resource.usage = max(10, min(95, resource.usage + (random.random() - 0.5) * 5))
        await broadcast_update()

async def update_agents_periodically():
    """Simulate agent status changes"""
    global agents_db
    while True:
        await asyncio.sleep(2)
        for agent in agents_db.values():
            if agent.status != AgentStatus.Terminated:
                agent.resource_usage["cpu"] = max(5, min(90, agent.resource_usage["cpu"] + (random.random() - 0.5) * 10))
                agent.resource_usage["gpu"] = max(2, min(95, agent.resource_usage["gpu"] + (random.random() - 0.5) * 15))
                agent.resource_usage["memory"] = max(10, min(80, agent.resource_usage["memory"] + (random.random() - 0.5) * 5))
        await broadcast_update()

async def broadcast_update():
    """Broadcast updates to all connected WebSocket clients"""
    update_data = {
        "type": "update",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": [agent.model_dump() for agent in agents_db.values()],
        "resources": [resource.model_dump() for resource in resources_db],
        "services": [service.model_dump() for service in services_db],
    }
    
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(update_data)
        except:
            disconnected.append(connection)
    
    # Remove disconnected clients
    for connection in disconnected:
        active_connections.remove(connection)

# REST API Endpoints

@app.get("/api/agents", response_model=List[AgentResponse])
async def get_agents():
    """Get all agents with status and resource usage"""
    return [agent for agent in agents_db.values()]

@app.get("/api/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get a specific agent by ID"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]

@app.post("/api/agents", response_model=AgentResponse)
async def create_agent(agent_data: AgentCreate):
    """Create a new agent"""
    agent_id = f"agent-{len(agents_db) + 1:03d}"
    new_agent = Agent(
        id=agent_id,
        name=agent_data.name,
        status=AgentStatus.Idle,
        resource_usage={"cpu": 0, "gpu": 0, "memory": 0}
    )
    agents_db[agent_id] = new_agent
    await broadcast_update()
    return new_agent

@app.post("/api/agents/{agent_id}/action")
async def agent_action(agent_id: str, action: AgentUpdate):
    """Perform an action on an agent (pause, resume, terminate)"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_db[agent_id]
    
    if action.status == AgentStatus.Paused:
        agent.status = AgentStatus.Paused
    elif action.status == AgentStatus.Running:
        agent.status = AgentStatus.Running
    elif action.status == AgentStatus.Terminated:
        agent.status = AgentStatus.Terminated
        agent.resource_usage = {"cpu": 0, "gpu": 0, "memory": 0}
    
    await broadcast_update()
    return {"message": f"Agent {agent_id} {action.status.value}"}

@app.get("/api/resources", response_model=List[ResourceResponse])
async def get_resources():
    """Get system resource metrics"""
    return resources_db

@app.get("/api/services", response_model=List[SystemServiceResponse])
async def get_services():
    """Get system service health status"""
    return services_db

# WebSocket endpoint for real-time updates

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.get("/")
async def root():
    return {"message": "AgenticOS Backend API", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}