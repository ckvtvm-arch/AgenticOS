from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import asyncio
import os
from typing import List, Dict, Optional

from .database import init_db
from .models import AgentStatus, Resource
from .schemas import AgentCreate, AgentUpdate, AgentResponse, ResourceResponse, SystemServiceResponse
from .runtime.manager import RuntimeManager

active_connections: List[WebSocket] = []
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    runtime_manager = RuntimeManager(backend_url=BACKEND_URL)
    runtime_manager.set_update_callback(lambda: asyncio.create_task(broadcast_update()))
    app.state.runtime_manager = runtime_manager
    await app.state.runtime_manager.start()

    app.state.runtime_manager.register_agent(
        name='CodeOptimizer',
        script_name='hello_agent.py',
        priority=10,
        capabilities=['optimization', 'analysis'],
        metadata={'version': '0.1', 'author': 'AgenticOS'},
    )
    app.state.runtime_manager.register_agent(
        name='DataAnalyzer',
        script_name='cpu_agent.py',
        priority=20,
        capabilities=['analysis', 'compute'],
        metadata={'version': '0.1', 'author': 'AgenticOS'},
    )

    yield

    for websocket in list(active_connections):
        await websocket.close()

app = FastAPI(
    title='AgenticOS Backend API',
    description='Backend API for AgenticOS Dashboard',
    version='0.2.0',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def get_runtime() -> RuntimeManager:
    runtime = getattr(app.state, 'runtime_manager', None)
    if runtime is None:
        raise RuntimeError('Runtime manager has not been initialized')
    return runtime


async def broadcast_update() -> None:
    runtime = get_runtime()
    update_data = {
        'type': 'update',
        'timestamp': datetime.utcnow().isoformat(),
        'agents': runtime.list_agents(),
        'resources': [resource.model_dump() for resource in runtime.get_resources()],
        'services': [service.model_dump() for service in runtime.get_services()],
    }

    disconnected: List[WebSocket] = []
    for connection in active_connections:
        try:
            await connection.send_json(update_data)
        except Exception:
            disconnected.append(connection)

    for connection in disconnected:
        if connection in active_connections:
            active_connections.remove(connection)


@app.get('/api/agents', response_model=List[AgentResponse])
async def get_agents():
    return [AgentResponse(**agent) for agent in get_runtime().list_agents()]


@app.get('/api/agents/{agent_id}', response_model=AgentResponse)
async def get_agent(agent_id: str):
    agent = get_runtime().get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail='Agent not found')
    return AgentResponse(**agent.to_dict())


@app.post('/api/agents', response_model=AgentResponse)
async def create_agent(agent_data: AgentCreate):
    script_name = agent_data.script_name or 'hello_agent.py'
    agent = get_runtime().register_agent(
        name=agent_data.name,
        script_name=script_name,
        priority=agent_data.priority or 50,
        capabilities=agent_data.capabilities or [],
        metadata=agent_data.metadata or {},
    )
    return AgentResponse(**agent.to_dict())


@app.post('/api/agents/{agent_id}/action')
async def agent_action(agent_id: str, action: AgentUpdate):
    result = get_runtime().action(agent_id, action.status)
    if result is None:
        raise HTTPException(status_code=404, detail='Agent not found')
    return {'message': f'Agent {agent_id} {action.status.value}'}


@app.post('/api/agents/{agent_id}/heartbeat')
async def agent_heartbeat(agent_id: str):
    result = get_runtime().heartbeat(agent_id)
    if result is None:
        raise HTTPException(status_code=404, detail='Agent not found')
    return {'message': 'Heartbeat received', 'agent_id': agent_id}


@app.get('/api/agents/discover', response_model=List[AgentResponse])
async def discover_agents(capability: str = Query(..., description='Capability to discover')):
    results = get_runtime().discover(capability)
    return [AgentResponse(**agent) for agent in results]


@app.get('/api/resources', response_model=List[ResourceResponse])
async def get_resources():
    return [ResourceResponse(**resource.model_dump()) for resource in get_runtime().get_resources()]


@app.get('/api/services', response_model=List[SystemServiceResponse])
async def get_services():
    return [SystemServiceResponse(**service.model_dump()) for service in get_runtime().get_services()]


@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)


@app.get('/')
async def root():
    return {'message': 'AgenticOS Backend API', 'version': '0.2.0'}


@app.get('/health')
async def health_check():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}