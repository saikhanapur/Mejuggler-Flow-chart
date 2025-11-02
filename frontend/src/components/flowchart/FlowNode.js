import React from 'react';

// Status configurations matching reference design
const STATUS_STYLES = {
  critical: {
    bg: 'bg-gradient-to-br from-red-500 to-red-600',
    text: 'text-white',
    icon: 'text-white',
    pulseClass: 'critical-highlight',
  },
  action: {
    bg: 'bg-white',
    border: 'border-blue-400',
    text: 'text-slate-800',
    icon: 'text-blue-600',
  },
  communication: {
    bg: 'bg-white',
    border: 'border-purple-400',
    text: 'text-slate-800',
    icon: 'text-purple-600',
  },
  operational: {
    bg: 'bg-white',
    border: 'border-emerald-400',
    text: 'text-slate-800',
    icon: 'text-emerald-600',
  },
  monitoring: {
    bg: 'bg-white',
    border: 'border-amber-400',
    text: 'text-slate-800',
    icon: 'text-amber-600',
  },
  verification: {
    bg: 'bg-white',
    border: 'border-teal-400',
    text: 'text-slate-800',
    icon: 'text-teal-600',
  },
  recovery: {
    bg: 'bg-white',
    border: 'border-green-400',
    text: 'text-slate-800',
    icon: 'text-green-600',
  },
};

// Status icons
const StatusIcon = ({ status }) => {
  const style = STATUS_STYLES[status] || STATUS_STYLES.action;
  const className = `w-5 h-5 ${style.icon}`;

  const icons = {
    critical: (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    action: (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    ),
    communication: (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    operational: (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    monitoring: (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    verification: (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    recovery: (
      <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
  };

  return icons[status] || icons.action;
};

const FlowNode = ({ node, onClick, isSelected }) => {
  const style = STATUS_STYLES[node.status] || STATUS_STYLES.action;
  const isCritical = node.status === 'critical';

  // Build class string
  const baseClasses = 'absolute transition-all duration-300 hover:scale-105 hover:shadow-2xl cursor-pointer rounded-xl p-4';
  const statusClasses = isCritical 
    ? `${style.bg} ${style.text} shadow-lg ${style.pulseClass}` 
    : `${style.bg} border-2 ${style.border} shadow-md`;
  const selectedClass = isSelected ? 'ring-4 ring-blue-400' : '';

  return (
    <div
      className={`${baseClasses} ${statusClasses} ${selectedClass}`}
      style={{
        left: `${node.x}px`,
        top: `${node.y}px`,
        width: '240px',
        minHeight: '80px',
      }}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          <StatusIcon status={node.status} />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className={`font-semibold text-sm leading-tight mb-1 ${isCritical ? 'text-white' : style.text}`}>
            {node.title}
          </h3>
          {node.description && (
            <p className={`text-xs leading-relaxed ${isCritical ? 'text-white opacity-90' : 'text-slate-600'}`}>
              {node.description.length > 100 ? `${node.description.substring(0, 100)}...` : node.description}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default FlowNode;
