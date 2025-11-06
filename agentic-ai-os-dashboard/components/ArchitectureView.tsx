import React from 'react';
import Card from './Card';

const architectureLayers = {
  kernel: {
    title: 'Kernel Layer',
    color: 'border-cyan-500',
    components: ['Agent Scheduler', 'Memory Manager', 'Agent Isolation Engine'],
  },
  systemServices: {
    title: 'System Services Layer',
    color: 'border-emerald-400',
    components: ['Agent Registry', 'Inference Engine', 'Context Management', 'Tool Execution', 'Communication Bus'],
  },
  userSpace: {
    title: 'User Space',
    color: 'border-amber-400',
    components: ['Agent Development Kit (ADK)', 'System Agent', 'Agent Orchestration'],
  },
};

const LayerCard: React.FC<{ layer: { title: string; color: string; components: string[] } }> = ({ layer }) => (
  <div className={`bg-gray-800/50 border-l-4 ${layer.color} p-4 rounded-r-lg`}>
    <h3 className="text-md font-semibold text-gray-100 mb-3">{layer.title}</h3>
    <div className="flex flex-wrap gap-2">
      {layer.components.map((component) => (
        <span key={component} className="bg-gray-700 text-gray-300 text-xs font-medium px-2.5 py-1 rounded-full">
          {component}
        </span>
      ))}
    </div>
  </div>
);

const ArchitectureView: React.FC = () => {
  return (
    <Card>
      <h2 className="text-lg font-semibold text-gray-100 mb-4">System Architecture</h2>
      <div className="space-y-4">
        <LayerCard layer={architectureLayers.userSpace} />
        <LayerCard layer={architectureLayers.systemServices} />
        <LayerCard layer={architectureLayers.kernel} />
      </div>
    </Card>
  );
};

export default ArchitectureView;
