import React from 'react';
import Card from './Card';
import { Agent, AgentStatus } from '../types';

interface AgentListProps {
  agents: Agent[];
}

const getStatusColor = (status: AgentStatus) => {
  switch (status) {
    case AgentStatus.Running:
      return 'bg-emerald-400';
    case AgentStatus.Idle:
      return 'bg-cyan-400';
    case AgentStatus.Paused:
      return 'bg-amber-400';
    case AgentStatus.Terminated:
      return 'bg-red-500';
    default:
      return 'bg-gray-500';
  }
};

const AgentList: React.FC<AgentListProps> = ({ agents }) => {
  return (
    <Card className="h-full">
      <h2 className="text-lg font-semibold text-gray-100 mb-4">Agent Processes</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-700">
          <thead className="bg-gray-800">
            <tr>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Agent Name</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">CPU %</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">GPU %</th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Memory %</th>
            </tr>
          </thead>
          <tbody className="bg-gray-800 divide-y divide-gray-700">
            {agents.map((agent) => (
              <tr key={agent.id} className="hover:bg-gray-700/50 transition-colors duration-150">
                <td className="px-4 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <span className={`h-2.5 w-2.5 rounded-full ${getStatusColor(agent.status)} ${agent.status === AgentStatus.Running ? 'animate-pulse-fast' : ''}`}></span>
                    <span className="ml-2 text-sm text-gray-300 hidden sm:inline">{agent.status}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-200">{agent.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{agent.resourceUsage.cpu.toFixed(1)}%</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{agent.resourceUsage.gpu.toFixed(1)}%</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{agent.resourceUsage.memory.toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

export default AgentList;
