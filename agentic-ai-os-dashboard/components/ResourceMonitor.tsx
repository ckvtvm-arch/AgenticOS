import React from 'react';
import Card from './Card';
// FIX: Import ResourceType to use it in the component.
import { Resource, ResourceType } from '../types';

interface ResourceMonitorProps {
  resource: Resource;
}

const ResourceMonitor: React.FC<ResourceMonitorProps> = ({ resource }) => {
  const { type, usage, total, unit, Icon } = resource;
  const usageColor = usage > 85 ? 'bg-red-500' : usage > 60 ? 'bg-amber-400' : 'bg-cyan-400';
  
  const formattedTotal = total > 10000 ? `${(total/1000).toFixed(0)}k` : total;
  const currentUsage = (total * (usage / 100)).toFixed(1);

  return (
    <Card>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
            <Icon className="h-6 w-6 text-gray-400" />
            <h3 className="text-md font-semibold text-gray-200">{type}</h3>
        </div>
        <span className="text-xl font-bold text-gray-100">{usage.toFixed(1)}%</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2.5 mb-2">
        <div className={`${usageColor} h-2.5 rounded-full`} style={{ width: `${usage}%` }}></div>
      </div>
       <div className="text-xs text-gray-400 text-right">
        {type === ResourceType.TokenBudget ? `${(parseInt(currentUsage, 10)/1000).toFixed(0)}k` : currentUsage} / {formattedTotal} {unit}
       </div>
    </Card>
  );
};

export default ResourceMonitor;