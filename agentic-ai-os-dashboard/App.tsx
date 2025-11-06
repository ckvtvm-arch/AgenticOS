import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import AgentList from './components/AgentList';
import ResourceMonitor from './components/ResourceMonitor';
import SystemStatus from './components/SystemStatus';
import ArchitectureView from './components/ArchitectureView';
import { Agent, Resource, SystemService, AgentStatus, ResourceType, SystemServiceStatus } from './types';
import { CpuChipIcon } from './components/icons/CpuChipIcon';
import { GpuChipIcon } from './components/icons/GpuChipIcon';
import { MemoryChipIcon } from './components/icons/MemoryChipIcon';
import { TokenIcon } from './components/icons/TokenIcon';

const App: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([
    { id: 'agent-001', name: 'CodeOptimizer', status: AgentStatus.Running, resourceUsage: { cpu: 25, gpu: 60, memory: 30 } },
    { id: 'agent-002', name: 'DataAnalyzer', status: AgentStatus.Running, resourceUsage: { cpu: 45, gpu: 75, memory: 50 } },
    { id: 'agent-003', name: 'SystemMonitor', status: AgentStatus.Idle, resourceUsage: { cpu: 5, gpu: 2, memory: 10 } },
    { id: 'agent-004', name: 'UITaskAutomator', status: AgentStatus.Paused, resourceUsage: { cpu: 10, gpu: 5, memory: 15 } },
    { id: 'agent-005', name: 'ResearchAggregator', status: AgentStatus.Terminated, resourceUsage: { cpu: 0, gpu: 0, memory: 0 } },
  ]);

  const [resources, setResources] = useState<Resource[]>([
    { type: ResourceType.CPU, usage: 45, total: 16, unit: 'Cores', Icon: CpuChipIcon },
    { type: ResourceType.GPU, usage: 78, total: 24, unit: 'GB VRAM', Icon: GpuChipIcon },
    { type: ResourceType.Memory, usage: 62, total: 64, unit: 'GB RAM', Icon: MemoryChipIcon },
    { type: ResourceType.TokenBudget, usage: 85, total: 1000000, unit: 'Tokens/hr', Icon: TokenIcon },
  ]);

  const [systemServices, setSystemServices] = useState<SystemService[]>([
    { name: 'Agent Registry', status: SystemServiceStatus.Online },
    { name: 'Inference Engine', status: SystemServiceStatus.Online },
    { name: 'Context Management', status: SystemServiceStatus.Degraded },
    { name: 'Tool Execution', status: SystemServiceStatus.Online },
    { name: 'Communication Bus', status: SystemServiceStatus.Offline },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate resource fluctuation
      setResources(prevResources =>
        prevResources.map(res => ({
          ...res,
          usage: Math.max(10, Math.min(95, res.usage + (Math.random() - 0.5) * 5)),
        }))
      );

      // Simulate agent status changes
      setAgents(prevAgents => 
        prevAgents.map(agent => {
            if (agent.status === AgentStatus.Terminated) return agent;
            const newCpu = Math.max(5, Math.min(90, agent.resourceUsage.cpu + (Math.random() - 0.5) * 10));
            const newGpu = Math.max(2, Math.min(95, agent.resourceUsage.gpu + (Math.random() - 0.5) * 15));
            const newMemory = Math.max(10, Math.min(80, agent.resourceUsage.memory + (Math.random() - 0.5) * 5));
            
            return {
                ...agent,
                resourceUsage: { cpu: newCpu, gpu: newGpu, memory: newMemory }
            };
        })
      );
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-300 font-sans">
      <Header />
      <main className="p-4 sm:p-6 lg:p-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          {resources.map((res) => (
            <ResourceMonitor key={res.type} resource={res} />
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <AgentList agents={agents} />
          </div>
          <div>
            <SystemStatus services={systemServices} />
          </div>
        </div>
        
        <div className="mt-6">
            <ArchitectureView />
        </div>
      </main>
    </div>
  );
};

export default App;