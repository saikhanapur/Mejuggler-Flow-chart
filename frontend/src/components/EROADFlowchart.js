import React, { useState } from 'react';

// Status color configurations
const STATUS_STYLES = {
  critical: {
    bg: 'bg-gradient-to-br from-red-500 to-red-600',
    border: 'border-red-400',
    text: 'text-white',
    icon: 'text-white',
    lineColor: '#ef4444',
  },
  action: {
    bg: 'bg-white',
    border: 'border-blue-400',
    text: 'text-slate-800',
    icon: 'text-blue-600',
    lineColor: '#3b82f6',
  },
  communication: {
    bg: 'bg-white',
    border: 'border-purple-400',
    text: 'text-slate-800',
    icon: 'text-purple-600',
    lineColor: '#a855f7',
  },
  operational: {
    bg: 'bg-white',
    border: 'border-emerald-400',
    text: 'text-slate-800',
    icon: 'text-emerald-600',
    lineColor: '#10b981',
  },
  monitoring: {
    bg: 'bg-white',
    border: 'border-amber-400',
    text: 'text-slate-800',
    icon: 'text-amber-600',
    lineColor: '#f59e0b',
  },
  verification: {
    bg: 'bg-white',
    border: 'border-teal-400',
    text: 'text-slate-800',
    icon: 'text-teal-600',
    lineColor: '#14b8a6',
  },
  recovery: {
    bg: 'bg-white',
    border: 'border-green-400',
    text: 'text-slate-800',
    icon: 'text-green-600',
    lineColor: '#22c55e',
  },
};

// Status icon component
const StatusIcon = ({ status }) => {
  const style = STATUS_STYLES[status] || STATUS_STYLES.action;
  const iconClass = `w-5 h-5 ${style.icon}`;
  
  const icons = {
    critical: (
      <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    action: (
      <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    ),
    communication: (
      <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    operational: (
      <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    monitoring: (
      <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    verification: (
      <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    recovery: (
      <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
  };
  
  return icons[status] || icons.action;
};

// Flow node component
const FlowNode = ({ node, onClick, isSelected }) => {
  const style = STATUS_STYLES[node.status] || STATUS_STYLES.action;
  const isCritical = node.status === 'critical';
  
  // FORCE consistent positioning
  const x = 330;
  const y = node.y || 0;
  
  return (
    <div
      className={`absolute transition-all duration-200 hover:scale-105 cursor-pointer ${
        isCritical 
          ? `${style.bg} ${style.text} shadow-lg` 
          : `${style.bg} border-2 ${style.border} shadow-md`
      } rounded-xl p-4 ${isSelected ? 'ring-4 ring-blue-400 shadow-xl' : ''}`}
      style={{
        left: `${x}px`,
        top: `${y}px`,
        width: '240px',
        minHeight: '80px',
      }}
      onClick={() => onClick(node)}
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
              {node.description}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

// Connection line component
const ConnectionLine = ({ from, to, color }) => {
  const fromX = 330 + 120; // Center of 240px node
  const fromY = (from.y || 0) + 60; // Bottom of node
  const toX = 330 + 120;
  const toY = (to.y || 0);
  
  const height = toY - fromY - 60;
  
  if (height <= 0) return null;
  
  return (
    <>
      {/* Vertical line */}
      <div
        className="absolute"
        style={{
          left: `${fromX}px`,
          top: `${fromY}px`,
          width: '2px',
          height: `${height}px`,
          backgroundColor: color,
        }}
      />
      {/* Arrow */}
      <div
        className="absolute"
        style={{
          left: `${fromX - 4}px`,
          top: `${toY - 10}px`,
          width: 0,
          height: 0,
          borderLeft: '4px solid transparent',
          borderRight: '4px solid transparent',
          borderTop: `8px solid ${color}`,
        }}
      />
    </>
  );
};

// Progress badge component
const ProgressBadge = ({ type, x, y, title, description }) => {
  const styles = {
    immediate: {
      bg: 'bg-red-50',
      border: 'border-red-300',
      titleColor: 'text-red-900',
      textColor: 'text-red-800',
      emoji: '⚠️',
    },
    ongoing: {
      bg: 'bg-amber-50',
      border: 'border-amber-300',
      titleColor: 'text-amber-900',
      textColor: 'text-amber-800',
      emoji: '🔄',
    },
    complete: {
      bg: 'bg-green-50',
      border: 'border-green-300',
      titleColor: 'text-green-900',
      textColor: 'text-green-800',
      emoji: '✅',
    },
  };
  
  const style = styles[type] || styles.immediate;
  
  return (
    <div
      className={`absolute ${style.bg} border-2 ${style.border} rounded-lg p-3 shadow-sm`}
      style={{ left: `${x}px`, top: `${y}px`, width: '200px' }}
    >
      <div className={`text-xs font-bold ${style.titleColor} mb-1`}>
        {style.emoji} {title}
      </div>
      <div className={`text-xs ${style.textColor}`}>
        {description}
      </div>
    </div>
  );
};

// Main component
const EROADFlowchart = ({ process, onNodeClick }) => {
  const [selectedNode, setSelectedNode] = useState(null);
  
  const handleNodeClick = (node) => {
    setSelectedNode(node);
    if (onNodeClick) {
      onNodeClick(node);
    }
  };
  
  // Normalize nodes: force X=330, Y=index*150
  const normalizedNodes = (process?.nodes || []).map((node, index) => ({
    ...node,
    x: 330,
    y: index * 150,
  }));
  
  // Calculate canvas height
  const maxY = normalizedNodes.length > 0 
    ? Math.max(...normalizedNodes.map(n => n.y || 0)) + 200 
    : 800;
  
  const canvasHeight = Math.max(maxY, 1000);
  
  // Extract quick reference data with validation
  const quickRef = process?.quickReference || {};
  const criticalActions = Array.isArray(quickRef.criticalActions) 
    ? quickRef.criticalActions 
    : [];
  const keyTimings = Array.isArray(quickRef.keyTimings)
    ? quickRef.keyTimings
    : [];
  const emergencyContacts = (typeof quickRef.emergencyContacts === 'object' && quickRef.emergencyContacts !== null)
    ? quickRef.emergencyContacts
    : {};
  
  return (
    <div className="w-full">
      {/* Legend */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6">
        <div className="flex flex-wrap items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <StatusIcon status="critical" />
            <span className="text-slate-700 font-medium">Critical</span>
          </div>
          <div className="flex items-center gap-2">
            <StatusIcon status="action" />
            <span className="text-slate-700 font-medium">Action Required</span>
          </div>
          <div className="flex items-center gap-2">
            <StatusIcon status="communication" />
            <span className="text-slate-700 font-medium">Communication</span>
          </div>
          <div className="flex items-center gap-2">
            <StatusIcon status="operational" />
            <span className="text-slate-700 font-medium">Operational</span>
          </div>
          <div className="flex items-center gap-2">
            <StatusIcon status="monitoring" />
            <span className="text-slate-700 font-medium">Monitoring</span>
          </div>
        </div>
      </div>
      
      {/* Flowchart Canvas */}
      <div 
        className="bg-white rounded-2xl shadow-xl border border-slate-200 p-12 relative overflow-auto"
        style={{ minHeight: `${canvasHeight}px` }}
      >
        {/* Grid Background */}
        <div 
          className="absolute inset-0 opacity-30 pointer-events-none"
          style={{
            backgroundImage: 'radial-gradient(circle, rgb(226, 232, 240) 1px, transparent 1px)',
            backgroundSize: '30px 30px',
          }}
        />
        
        {/* Connection Lines */}
        {normalizedNodes.map((node, index) => {
          if (index === normalizedNodes.length - 1) return null;
          const nextNode = normalizedNodes[index + 1];
          const style = STATUS_STYLES[nextNode.status] || STATUS_STYLES.action;
          
          return (
            <ConnectionLine
              key={`line-${index}`}
              from={node}
              to={nextNode}
              color={style.lineColor}
            />
          );
        })}
        
        {/* Nodes */}
        {normalizedNodes.map((node) => (
          <FlowNode
            key={node.id}
            node={node}
            onClick={handleNodeClick}
            isSelected={selectedNode?.id === node.id}
          />
        ))}
        
        {/* Progress Badges */}
        {(process?.progressStages || []).map((stage, idx) => (
          <ProgressBadge
            key={idx}
            type={stage.type}
            x={630}
            y={stage.y || 0}
            title={stage.title}
            description={stage.description}
          />
        ))}
      </div>
      
      {/* Quick Reference */}
      <div className="grid grid-cols-3 gap-6 mt-6">
        {/* Critical Actions */}
        <div className="bg-gradient-to-br from-red-50 to-red-100 border-2 border-red-300 rounded-xl p-6 shadow-lg">
          <h3 className="font-bold text-red-900 mb-4 flex items-center gap-2 text-lg">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Critical Actions
          </h3>
          <div className="space-y-2 text-sm text-red-800">
            {criticalActions.length > 0 ? (
              criticalActions.map((action, idx) => (
                <div key={idx}>• {action}</div>
              ))
            ) : (
              <div>• No critical actions identified</div>
            )}
          </div>
        </div>
        
        {/* Key Timings */}
        <div className="bg-gradient-to-br from-amber-50 to-amber-100 border-2 border-amber-300 rounded-xl p-6 shadow-lg">
          <h3 className="font-bold text-amber-900 mb-4 flex items-center gap-2 text-lg">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Key Timings
          </h3>
          <div className="space-y-2 text-sm text-amber-800">
            {keyTimings.length > 0 ? (
              keyTimings.map((timing, idx) => (
                <div key={idx}>• {timing}</div>
              ))
            ) : (
              <div>• No specific timings mentioned</div>
            )}
          </div>
        </div>
        
        {/* Recovery Steps */}
        <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-2 border-emerald-300 rounded-xl p-6 shadow-lg">
          <h3 className="font-bold text-emerald-900 mb-4 flex items-center gap-2 text-lg">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Recovery Steps
          </h3>
          <div className="space-y-2 text-sm text-emerald-800">
            {normalizedNodes
              .filter(n => n.status === 'recovery' || n.status === 'verification')
              .map((node, idx) => (
                <div key={idx}>• {node.title}</div>
              ))
            }
            {normalizedNodes.filter(n => n.status === 'recovery').length === 0 && (
              <div>• Complete process and document</div>
            )}
          </div>
        </div>
      </div>
      
      {/* Emergency Contacts */}
      {Object.keys(emergencyContacts).length > 0 && (
        <div className="mt-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-xl p-8 shadow-xl">
          <h3 className="font-bold text-blue-900 mb-6 text-2xl flex items-center gap-3">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            Emergency Contacts
          </h3>
          <div className="grid grid-cols-3 gap-6">
            {Object.entries(emergencyContacts).map(([name, contact], idx) => (
              <div key={idx} className="bg-white/70 rounded-lg p-5 border border-blue-200">
                <h4 className="font-semibold text-blue-900 mb-3">{name}</h4>
                <div className="text-sm text-blue-800">
                  <p className="font-mono">{contact}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default EROADFlowchart;
