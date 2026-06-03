import React, { useState, useEffect, useRef } from 'react';
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

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

const App: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [systemServices, setSystemServices] = useState<SystemService[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Fetch initial data from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [agentsRes, resourcesRes, servicesRes] = await Promise.all([
          fetch(`${API_URL}/api/agents`),
          fetch(`${API_URL}/api/resources`),
          fetch(`${API_URL}/api/services`),
        ]);

        if (!agentsRes.ok || !resourcesRes.ok || !servicesRes.ok) {
          throw new Error('Failed to fetch data from backend');
        }

        const agentsData = await agentsRes.json();
        const resourcesData = await resourcesRes.json();
        const servicesData = await servicesRes.json();

        // Map API data to component types
        setAgents(agentsData.map((agent: any) => ({
          id: agent.id,
          name: agent.name,
          status: agent.status,
          resourceUsage: agent.resource_usage,
        })));

        setResources(resourcesData.map((res: any) => ({
          type: res.type,
          usage: res.usage,
          total: res.total,
          unit: res.unit,
          Icon: getResourceIcon(res.type),
        })));

        setSystemServices(servicesData.map((service: any) => ({
          name: service.name,
          status: service.status,
        })));

      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        wsRef.current = new WebSocket(WS_URL);

        wsRef.current.onopen = () => {
          console.log('WebSocket connected');
        };

        wsRef.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'update') {
              // Update agents
              if (data.agents) {
                setAgents(data.agents.map((agent: any) => ({
                  id: agent.id,
                  name: agent.name,
                  status: agent.status,
                  resourceUsage: agent.resource_usage,
                })));
              }

              // Update resources
              if (data.resources) {
                setResources(data.resources.map((res: any) => ({
                  type: res.type,
                  usage: res.usage,
                  total: res.total,
                  unit: res.unit,
                  Icon: getResourceIcon(res.type),
                })));
              }

              // Update services
              if (data.services) {
                setSystemServices(data.services.map((service: any) => ({
                  name: service.name,
                  status: service.status,
                })));
              }
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
          }
        };

        wsRef.current.onerror = (err) => {
          console.error('WebSocket error:', err);
        };

        wsRef.current.onclose = () => {
          console.log('WebSocket disconnected, attempting to reconnect...');
          setTimeout(connectWebSocket, 3000);
        };
      } catch (err) {
        console.error('Failed to connect WebSocket:', err);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const getResourceIcon = (type: string) => {
    switch (type) {
      case 'CPU':
        return CpuChipIcon;
      case 'GPU':
        return GpuChipIcon;
      case 'Memory':
        return MemoryChipIcon;
      case 'Token Budget':
        return TokenIcon;
      default:
        return CpuChipIcon;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-300 font-sans">
      <Header />
      <main className="p-4 sm:p-6 lg:p-8">
        {loading && (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4"></div>
              <p className="text-gray-400">Loading dashboard data...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-red-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-red-300">{error}</span>
            </div>
            <p className="text-sm text-gray-400 mt-2">Make sure the backend server is running on {API_URL}</p>
          </div>
        )}

        {!loading && !error && (
          <>
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
          </>
        )}
      </main>
    </div>
  );
};

export default App;