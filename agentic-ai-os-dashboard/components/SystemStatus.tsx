import React from 'react';
import Card from './Card';
import { SystemService, SystemServiceStatus } from '../types';
import { StatusOnlineIcon } from './icons/StatusOnlineIcon';
import { StatusWarningIcon } from './icons/StatusWarningIcon';
import { StatusOfflineIcon } from './icons/StatusOfflineIcon';


const getStatusIcon = (status: SystemServiceStatus) => {
    switch (status) {
        case SystemServiceStatus.Online:
            return <StatusOnlineIcon className="h-5 w-5 text-emerald-400" />;
        case SystemServiceStatus.Degraded:
            return <StatusWarningIcon className="h-5 w-5 text-amber-400" />;
        case SystemServiceStatus.Offline:
            return <StatusOfflineIcon className="h-5 w-5 text-red-500" />;
        default:
            return null;
    }
};

const getStatusTextColor = (status: SystemServiceStatus) => {
    switch (status) {
        case SystemServiceStatus.Online:
            return 'text-emerald-400';
        case SystemServiceStatus.Degraded:
            return 'text-amber-400';
        case SystemServiceStatus.Offline:
            return 'text-red-500';
        default:
            return 'text-gray-400';
    }
};

interface SystemStatusProps {
    services: SystemService[];
}

const SystemStatus: React.FC<SystemStatusProps> = ({ services }) => {
    return (
        <Card className="h-full">
            <h2 className="text-lg font-semibold text-gray-100 mb-4">System Services</h2>
            <ul className="space-y-3">
                {services.map((service) => (
                    <li key={service.name} className="flex items-center justify-between">
                        <span className="text-sm text-gray-300">{service.name}</span>
                        <div className="flex items-center space-x-2">
                           {getStatusIcon(service.status)}
                           <span className={`text-sm font-medium ${getStatusTextColor(service.status)}`}>
                               {service.status}
                           </span>
                        </div>
                    </li>
                ))}
            </ul>
        </Card>
    );
};

export default SystemStatus;