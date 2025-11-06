import React from 'react';

export enum AgentStatus {
  Running = 'Running',
  Paused = 'Paused',
  Idle = 'Idle',
  Terminated = 'Terminated',
}

export enum ResourceType {
  CPU = 'CPU',
  GPU = 'GPU',
  Memory = 'Memory',
  TokenBudget = 'Token Budget',
}

export enum SystemServiceStatus {
    Online = 'Online',
    Degraded = 'Degraded',
    Offline = 'Offline'
}

export interface AgentResourceUsage {
  cpu: number; // percentage
  gpu: number; // percentage
  memory: number; // percentage
}

export interface Agent {
  id: string;
  name: string;
  status: AgentStatus;
  resourceUsage: AgentResourceUsage;
}

export interface Resource {
  type: ResourceType;
  usage: number; // percentage
  total: number;
  unit: string;
  Icon: React.ElementType;
}

export interface SystemService {
    name: string;
    status: SystemServiceStatus;
}
