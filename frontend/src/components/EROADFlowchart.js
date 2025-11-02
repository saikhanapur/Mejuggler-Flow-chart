import React, { useState } from 'react';

// Status color configurations
const STATUS_STYLES = {
  critical: {
    bg: 'bg-gradient-to-br from-red-500 to-red-600',
    border: 'border-red-400',
    text: 'text-white',
    icon: 'text-white',
    line: 'rgb(239, 68, 68)', // red-500
  },
  action: {
    bg: 'bg-white',
    border: 'border-blue-400',
    text: 'text-slate-800',
    icon: 'text-blue-600',
    line: 'rgb(96, 165, 250)', // blue-400
  },
  communication: {
    bg: 'bg-white',
    border: 'border-purple-400',
    text: 'text-slate-800',
    icon: 'text-purple-600',
    line: 'rgb(168, 85, 247)', // purple-500
  },
  operational: {
    bg: 'bg-white',
    border: 'border-emerald-400',
    text: 'text-slate-800',
    icon: 'text-emerald-600',
    line: 'rgb(16, 185, 129)', // emerald-500
  },
  monitoring: {
    bg: 'bg-white',
    border: 'border-amber-400',
    text: 'text-slate-800',
    icon: 'text-amber-600',
    line: 'rgb(245, 158, 11)', // amber-500
  },
  verification: {
    bg: 'bg-white',
    border: 'border-teal-400',
    text: 'text-slate-800',
    icon: 'text-teal-600',
    line: 'rgb(20, 184, 166)', // teal-500
  },
  recovery: {
    bg: 'bg-white',
    border: 'border-green-400',
    text: 'text-slate-800',
    icon: 'text-green-600',
    line: 'rgb(34, 197, 94)', // green-500
  },
};

// Status icons matching reference design
const StatusIcon = ({ status }) => {
  const colorClass = STATUS_COLORS[status]?.icon || 'text-slate-600';
  
  const icons = {
    critical: (
      <svg className={`w-5 h-5 ${colorClass}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    action: (
      <svg className={`w-5 h-5 ${colorClass}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    ),
    communication: (
      <svg className={`w-5 h-5 ${colorClass}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    operational: (
      <svg className={`w-5 h-5 ${colorClass}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
      </svg>
    ),
    monitoring: (
      <svg className={`w-5 h-5 ${colorClass}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    verification: (
      <svg className={`w-5 h-5 ${colorClass}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    recovery: (
      <svg className={`w-5 h-5 ${colorClass}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
  };
  
  return icons[status] || icons.action;
};

// Node Card Component
const FlowNode = ({ node, onClick, isSelected }) => {
  const colors = STATUS_COLORS[node.status] || STATUS_COLORS.action;
  const isCritical = node.status === 'critical';
  
  // ============ FIX #3: NORMALIZE COORDINATES (DEFENSE IN DEPTH) ============
  // Ensure valid positioning even if backend sends incorrect coordinates
  // Check both flat (node.x) and nested (node.position.x) formats
  const nodeX = node.x !== undefined ? node.x : (node.position?.x || 330);
  const nodeY = node.y !== undefined ? node.y : (node.position?.y || 0);
  
  const normalizedX = (nodeX !== null && nodeX >= 0) ? nodeX : 330;
  const normalizedY = (nodeY !== null && nodeY >= 0) ? nodeY : 0;
  
  // DEBUG
  if (normalizedX !== 330 || normalizedY < 0 || normalizedY > 2000) {
    console.warn('⚠️ Node positioning issue:', { 
      id: node.id, 
      title: node.title,
      nodeX, 
      nodeY, 
      normalizedX, 
      normalizedY,
      hasX: node.x !== undefined,
      hasPosition: !!node.position
    });
  }
  // ============ END FIX #3 ============
  
  return (
    <div
      className={`absolute transition-all duration-300 hover:scale-105 hover:shadow-2xl cursor-pointer ${
        isCritical 
          ? `${colors.bg} text-white shadow-lg` 
          : `${colors.bg} border-2 ${colors.border} shadow-md`
      } rounded-xl p-4 ${isSelected ? 'ring-4 ring-blue-400' : ''}`}
      style={{
        left: `${normalizedX}px`,
        top: `${normalizedY}px`,
        width: '240px',
      }}
      onClick={() => onClick(node)}
    >
      <div className="flex items-start gap-3">
        <div className="mt-0.5">
          <StatusIcon status={node.status} />
        </div>
        <h3 className={`font-semibold text-sm leading-tight ${isCritical ? 'text-white' : colors.text}`}>
          {node.title}
        </h3>
      </div>
    </div>
  );
};

// Connection Line Components - Smart Routing
const SimpleVerticalLine = ({ from, to, color, dashed }) => {
  const height = to.y - from.y - 60;
  
  const lineStyle = {
    left: `${from.x + 120}px`, // Center of 240px wide node
    top: `${from.y + 60}px`,
    width: '2px',
    height: `${height}px`,
    backgroundColor: dashed ? 'transparent' : color,
    backgroundImage: dashed 
      ? `repeating-linear-gradient(${color} 0px, ${color} 4px, transparent 4px, transparent 8px)`
      : 'none',
  };
  
  const arrowStyle = {
    left: `${from.x + 117}px`,
    top: `${to.y - 10}px`,
    borderLeft: '4px solid transparent',
    borderRight: '4px solid transparent',
    borderTop: `8px solid ${color}`,
  };
  
  return (
    <>
      <div className="absolute" style={lineStyle} />
      {!dashed && <div className="absolute w-0 h-0" style={arrowStyle} />}
    </>
  );
};

const DecisionBranchLine = ({ from, to, color, dashed }) => {
  // L-shaped connection: vertical down, horizontal across, vertical down to target
  const midY = from.y + 80;
  const verticalHeight1 = midY - from.y - 60;
  const horizontalWidth = Math.abs(to.x - from.x);
  const verticalHeight2 = to.y - midY;
  
  const isLeftBranch = to.x < from.x;
  
  return (
    <>
      {/* Vertical segment 1: from source node down */}
      <div 
        className="absolute" 
        style={{
          left: `${from.x + 120}px`,
          top: `${from.y + 60}px`,
          width: '2px',
          height: `${verticalHeight1}px`,
          backgroundColor: dashed ? 'transparent' : color,
          backgroundImage: dashed 
            ? `repeating-linear-gradient(${color} 0px, ${color} 4px, transparent 4px, transparent 8px)`
            : 'none',
        }}
      />
      
      {/* Horizontal segment: across */}
      <div 
        className="absolute" 
        style={{
          left: isLeftBranch ? `${to.x + 120}px` : `${from.x + 120}px`,
          top: `${midY}px`,
          width: `${horizontalWidth}px`,
          height: '2px',
          backgroundColor: dashed ? 'transparent' : color,
          backgroundImage: dashed 
            ? `repeating-linear-gradient(to right, ${color} 0px, ${color} 4px, transparent 4px, transparent 8px)`
            : 'none',
        }}
      />
      
      {/* Vertical segment 2: down to target */}
      <div 
        className="absolute" 
        style={{
          left: `${to.x + 120}px`,
          top: `${midY}px`,
          width: '2px',
          height: `${verticalHeight2}px`,
          backgroundColor: dashed ? 'transparent' : color,
          backgroundImage: dashed 
            ? `repeating-linear-gradient(${color} 0px, ${color} 4px, transparent 4px, transparent 8px)`
            : 'none',
        }}
      />
      
      {/* Arrow at target */}
      {!dashed && (
        <div 
          className="absolute w-0 h-0" 
          style={{
            left: `${to.x + 117}px`,
            top: `${to.y - 10}px`,
            borderLeft: '4px solid transparent',
            borderRight: '4px solid transparent',
            borderTop: `8px solid ${color}`,
          }}
        />
      )}
    </>
  );
};

const ConnectionLine = ({ from, to, color, dashed = false }) => {
  const deltaX = Math.abs(to.x - from.x);
  
  // If nodes are vertically aligned (deltaX < 50px), use simple vertical line
  if (deltaX < 50) {
    return <SimpleVerticalLine from={from} to={to} color={color} dashed={dashed} />;
  }
  
  // If nodes are horizontally offset (deltaX >= 50px), use L-shaped branch
  return <DecisionBranchLine from={from} to={to} color={color} dashed={dashed} />;
};

// Progress Stage Badge Component
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
      className={`absolute ${style.bg} border-2 ${style.border} rounded-lg p-3`}
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

// Main EROAD Flowchart Component
const EROADFlowchart = ({ process, onNodeClick }) => {
  const [selectedNode, setSelectedNode] = useState(null);
  
  const handleNodeClick = (node) => {
    setSelectedNode(node);
    if (onNodeClick) {
      onNodeClick(node);
    }
  };
  
  // ============ FIX #4: VALIDATE QUICK REFERENCE DATA ============
  // Defensive validation to prevent rendering errors with missing/malformed data
  const quickRef = process.quickReference || {};
  const criticalActions = Array.isArray(quickRef.criticalActions) 
    ? quickRef.criticalActions 
    : [];
  const keyTimings = Array.isArray(quickRef.keyTimings)
    ? quickRef.keyTimings
    : [];
  const emergencyContacts = (typeof quickRef.emergencyContacts === 'object' && quickRef.emergencyContacts !== null && !Array.isArray(quickRef.emergencyContacts))
    ? quickRef.emergencyContacts
    : {};
  // ============ END FIX #4 ============
  
  // Calculate canvas height based on nodes (with safety checks)
  const nodes = process.nodes || [];
  const maxY = nodes.length > 0 
    ? Math.max(...nodes.map(n => n.y || 0)) + 200 
    : 1800;
  const canvasHeight = Math.max(maxY, 1800);
  
  // DEBUG: Log node coordinates
  console.log('🎨 EROAD Flowchart Rendering:', {
    nodeCount: nodes.length,
    canvasHeight,
    maxY,
    nodes: nodes.map(n => ({ id: n.id, title: n.title, x: n.x, y: n.y }))
  });
  
  // Safety check - don't render if no nodes
  if (!nodes || nodes.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-white rounded-xl p-12">
        <div className="text-center">
          <div className="text-slate-400 text-lg mb-2">No flowchart data available</div>
          <div className="text-slate-500 text-sm">The process may still be generating...</div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="w-full">
      {/* Legend/Status Bar */}
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
        className="bg-white rounded-2xl shadow-xl border border-slate-200 p-12 relative"
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
        
        {/* Render Connection Lines */}
        {process.edges && process.edges.map((edge, idx) => {
          const fromNode = process.nodes.find(n => n.id === edge.source);
          const toNode = process.nodes.find(n => n.id === edge.target);
          
          if (!fromNode || !toNode) return null;
          
          // Normalize coordinates for connection lines too
          const fromX = (fromNode.x && fromNode.x > 0) ? fromNode.x : 330;
          const fromY = (fromNode.y !== undefined && fromNode.y >= 0) ? fromNode.y : 0;
          const toX = (toNode.x && toNode.x > 0) ? toNode.x : 330;
          const toY = (toNode.y !== undefined && toNode.y >= 0) ? toNode.y : 0;
          
          const color = STATUS_COLORS[toNode.status]?.line || 'rgb(148, 163, 184)';
          const dashed = edge.type === 'dashed';
          
          return (
            <ConnectionLine
              key={idx}
              from={{ x: fromX, y: fromY }}
              to={{ x: toX, y: toY }}
              color={color}
              dashed={dashed}
            />
          );
        })}
        
        {/* Render Nodes */}
        {process.nodes && process.nodes.map((node) => (
          <FlowNode
            key={node.id}
            node={node}
            onClick={handleNodeClick}
            isSelected={selectedNode?.id === node.id}
          />
        ))}
        
        {/* Progress Stage Badges */}
        {process.progressStages && process.progressStages.map((stage, idx) => (
          <ProgressBadge
            key={idx}
            type={stage.type}
            x={stage.x}
            y={stage.y}
            title={stage.title}
            description={stage.description}
          />
        ))}
      </div>
      
      {/* Quick Reference Panels */}
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
            {process.nodes && process.nodes
              .filter(n => n.status === 'recovery' || n.status === 'verification')
              .map((node, idx) => (
                <div key={idx}>• {node.title}</div>
              ))
            }
            {(!process.nodes || process.nodes.filter(n => n.status === 'recovery').length === 0) && (
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
            Emergency Contacts Quick Reference
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
