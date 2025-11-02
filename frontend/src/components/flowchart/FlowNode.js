import React from 'react';

// Status configurations matching reference design
const STATUS_CONFIG = {
  trigger: {
    container: 'bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/50',
    icon: 'text-white',
    pulse: true,
  },
  critical: {
    container: 'bg-gradient-to-br from-rose-500 to-rose-600 text-white shadow-lg shadow-rose-500/50',
    icon: 'text-white',
    pulse: true,
  },
  action: {
    container: 'bg-white border-2 border-blue-400 shadow-md hover:border-blue-500',
    icon: 'text-blue-500',
  },
  communication: {
    container: 'bg-white border-2 border-purple-400 shadow-md hover:border-purple-500',
    icon: 'text-purple-500',
  },
  operational: {
    container: 'bg-white border-2 border-emerald-400 shadow-md hover:border-emerald-500',
    icon: 'text-emerald-500',
  },
  monitoring: {
    container: 'bg-white border-2 border-amber-400 shadow-md hover:border-amber-500',
    icon: 'text-amber-500',
  },
  verification: {
    container: 'bg-white border-2 border-teal-400 shadow-md hover:border-teal-500',
    icon: 'text-teal-500',
  },
  recovery: {
    container: 'bg-white border-2 border-green-400 shadow-md hover:border-green-500',
    icon: 'text-green-500',
  },
  warning: {
    container: 'bg-white border-2 border-amber-400 shadow-md hover:border-amber-500',
    icon: 'text-amber-500',
  },
};

// Status icons
const StatusIcon = ({ status }) => {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.operational;
  const className = `w-5 h-5 ${config.icon}`;

  switch (status) {
    case 'trigger':
      return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      );
    case 'critical':
      return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    case 'action':
      return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      );
    case 'communication':
      return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      );
    case 'operational':
      return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    case 'monitoring':
    case 'warning':
      return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    case 'verification':
      return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      );
    case 'recovery':
      return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      );
    default:
      return (
        <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
  }
};

const FlowNode = ({ node, onClick, isSelected }) => {
  const config = STATUS_CONFIG[node.status] || STATUS_CONFIG.operational;
  
  // Get coordinates from node (backend provides these)
  const x = node.x || node.position?.x || 0;
  const y = node.y || node.position?.y || 0;

  return (
    <div
      data-testid={`flow-node-${node.id}`}
      className={`absolute transition-all duration-300 hover:scale-105 hover:shadow-2xl cursor-pointer rounded-xl p-4 ${
        config.container
      } ${config.pulse ? 'animate-pulse-glow' : ''} ${isSelected ? 'ring-4 ring-blue-400' : ''}`}
      style={{
        left: `${x}px`,
        top: `${y}px`,
        width: '240px',
        minHeight: '80px',
        zIndex: 10,
      }}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div className="mt-0.5">
          <StatusIcon status={node.status} />
        </div>
        <div className="flex-1">
          <h3 
            className="font-semibold text-sm leading-tight break-words"
            style={{ fontFamily: 'Inter, sans-serif' }}
          >
            {node.title}
          </h3>
        </div>
      </div>
    </div>
  );
};

export default FlowNode;
