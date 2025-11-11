import React, { useState } from 'react';

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

const FlowNode = ({ node, onClick, onUpdateNode, isSelected, selectedNodeId, isOnCriticalPath }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editedTitle, setEditedTitle] = useState(node.title);
  
  const config = STATUS_CONFIG[node.status] || STATUS_CONFIG.operational;
  
  // Get coordinates from node (backend provides these)
  const x = node.x || node.position?.x || 0;
  const y = node.y || node.position?.y || 0;

  // Check node type
  const isDecision = node.isDecisionPoint || false;
  const isMerge = node.isMergePoint || false;
  const isCritical = node.status === 'critical' || node.status === 'trigger';
  const isLoop = node.isLoop || false;
  const hasGap = node.operationalDetails?.gap || false;
  
  // Check if node has sub-steps to show
  const subSteps = node.operationalDetails?.specificActions || node.subSteps || [];
  const hasSubSteps = subSteps.length > 0;
  
  // Handle expand/collapse (prevent event bubbling to onClick)
  const handleExpandToggle = (e) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };
  
  // Handle title edit
  const handleTitleEdit = (e) => {
    e.stopPropagation();
    setIsEditingTitle(true);
  };
  
  const handleTitleSave = async (e) => {
    e.stopPropagation();
    if (editedTitle.trim() && editedTitle !== node.title) {
      if (onUpdateNode) {
        await onUpdateNode(node.id, 'title', editedTitle.trim());
      }
    }
    setIsEditingTitle(false);
  };
  
  const handleTitleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleTitleSave(e);
    } else if (e.key === 'Escape') {
      setEditedTitle(node.title);
      setIsEditingTitle(false);
    }
  };

  // Decision nodes still render as diamonds
  if (isDecision) {
    return (
      <div
        data-testid={`flow-node-${node.id}`}
        className="absolute"
        style={{
          left: `${x}px`,
          top: `${y}px`,
          width: '200px',
          height: '200px',
          zIndex: 10,
        }}
        onClick={onClick}
      >
        {/* Diamond shape using SVG */}
        <svg 
          width="200" 
          height="200" 
          className="cursor-pointer transition-all duration-300 hover:scale-105"
          style={{ filter: isSelected ? 'drop-shadow(0 0 10px rgba(59, 130, 246, 0.8))' : 'drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1))' }}
        >
          {/* Diamond path */}
          <path
            d="M 100 10 L 190 100 L 100 190 L 10 100 Z"
            fill="url(#yellowGradient)"
            stroke="#f59e0b"
            strokeWidth="3"
            className="transition-all duration-300"
          />
          <defs>
            <linearGradient id="yellowGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#fbbf24" />
              <stop offset="100%" stopColor="#f59e0b" />
            </linearGradient>
          </defs>
          
          {/* Icon */}
          <g transform="translate(80, 80)">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
              <path d="M9 18l6-6-6-6" />
              <path d="M15 18l6-6-6-6" />
            </svg>
          </g>
          
          {/* Text */}
          <text
            x="100"
            y="120"
            textAnchor="middle"
            fill="white"
            fontSize="13"
            fontWeight="600"
            fontFamily="Inter, sans-serif"
          >
            {node.title.length > 25 ? node.title.substring(0, 25) + '...' : node.title}
          </text>
        </svg>
      </div>
    );
  }

  // ALL other nodes use consistent rounded rectangle shape
  // Differentiate by: border thickness, shadow size, colors, gap indicator, critical path
  const borderStyle = isCritical ? 'border-4' : 'border-2';
  const shadowStyle = isCritical ? 'shadow-2xl' : 'shadow-lg';
  const gapBorderStyle = hasGap ? 'border-l-4 border-l-amber-500' : '';
  const criticalPathStyle = isOnCriticalPath ? 'ring-4 ring-red-500 ring-offset-2' : '';
  
  return (
    <div
      data-testid={`flow-node-${node.id}`}
      className={`absolute transition-all duration-300 hover:scale-105 hover:shadow-2xl cursor-pointer rounded-xl p-4 ${
        config.container
      } ${borderStyle} ${shadowStyle} ${gapBorderStyle} ${config.pulse ? 'animate-pulse-glow' : ''} ${
        isSelected ? 'ring-4 ring-blue-400 ring-offset-2' : ''
      } ${isMerge ? 'ring-2 ring-purple-400 ring-offset-2' : ''} ${criticalPathStyle}`}
      style={{
        left: `${x}px`,
        top: `${y}px`,
        width: '240px',
        minHeight: isExpanded ? 'auto' : '80px',
        maxHeight: isExpanded ? '400px' : '120px',
        overflow: isExpanded ? 'visible' : 'hidden',
        zIndex: isExpanded ? 20 : 10, // Bring expanded nodes to front
      }}
      onClick={onClick}
    >
      {/* Gap indicator badge */}
      {hasGap && (
        <div className="absolute -top-3 -left-3 bg-amber-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow-lg flex items-center gap-1">
          <span>⚠️</span>
          <span>GAP</span>
        </div>
      )}
      
      {/* Loop indicator badge */}
      {isLoop && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-green-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow-lg flex items-center gap-1">
          <span>↻</span>
          <span>LOOP</span>
        </div>
      )}
      
      {/* Merge indicator badge */}
      {isMerge && (
        <div className="absolute -top-3 -right-3 bg-purple-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow-lg">
          MERGE
        </div>
      )}
      
      {/* Time estimate badge - if available */}
      {node.operationalDetails?.estimatedDuration && (
        <div 
          className={`absolute ${node.priority ? 'top-6' : '-top-2'} -right-2 bg-slate-100 text-slate-700 text-xs font-semibold px-2 py-1 rounded-full border border-slate-300 shadow-sm flex items-center gap-1`}
        >
          <span>⏱️</span>
          <span>{node.operationalDetails.estimatedDuration}</span>
        </div>
      )}
      
      {/* AI Recommendations badges - bottom right */}
      {node.aiRecommendations && (
        <div className="absolute -bottom-2 -right-2 flex gap-1">
          {/* Automation Score Badge */}
          {node.aiRecommendations.automationScore > 0 && (
            <div 
              className={`text-xs font-bold px-2 py-1 rounded-full shadow-md flex items-center gap-1 ${
                node.aiRecommendations.automationScore >= 80 ? 'bg-green-500 text-white' :
                node.aiRecommendations.automationScore >= 50 ? 'bg-yellow-500 text-white' :
                'bg-gray-400 text-white'
              }`}
              title={`Automation Potential: ${node.aiRecommendations.automationScore}%`}
            >
              <span>🤖</span>
              <span>{node.aiRecommendations.automationScore}</span>
            </div>
          )}
          
          {/* Bottleneck Risk Badge */}
          {node.aiRecommendations.bottleneckRisk > 40 && (
            <div 
              className={`text-xs font-bold px-2 py-1 rounded-full shadow-md flex items-center gap-1 ${
                node.aiRecommendations.bottleneckRisk >= 80 ? 'bg-red-500 text-white' :
                node.aiRecommendations.bottleneckRisk >= 60 ? 'bg-orange-500 text-white' :
                'bg-yellow-500 text-white'
              }`}
              title={`Bottleneck Risk: ${node.aiRecommendations.bottleneckRisk}%`}
            >
              <span>⚠️</span>
              <span>{node.aiRecommendations.bottleneckRisk}</span>
            </div>
          )}
        </div>
      )}
      
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex-shrink-0">
          <StatusIcon status={node.status} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            {isEditingTitle ? (
              <input
                type="text"
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
                onBlur={handleTitleSave}
                onKeyDown={handleTitleKeyDown}
                onClick={(e) => e.stopPropagation()}
                className="font-semibold text-sm leading-tight break-words flex-1 border-2 border-blue-400 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                style={{ fontFamily: 'Inter, sans-serif' }}
                autoFocus
              />
            ) : (
              <h3 
                className="font-semibold text-sm leading-tight break-words flex-1 hover:bg-blue-50 hover:cursor-text rounded px-2 py-1 -mx-2 -my-1 transition-colors group"
                style={{ fontFamily: 'Inter, sans-serif' }}
                onClick={handleTitleEdit}
                title="Click to edit"
              >
                {node.title}
                <svg className="inline-block w-3 h-3 ml-1 opacity-0 group-hover:opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </h3>
            )}
            
            {/* Expand/Collapse button if node has sub-steps */}
            {hasSubSteps && (
              <button
                onClick={handleExpandToggle}
                className="flex-shrink-0 p-1 hover:bg-black/10 rounded transition-colors"
                title={isExpanded ? "Collapse details" : "Expand details"}
              >
                <svg 
                  className={`w-4 h-4 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            )}
          </div>
          
          {/* Expandable sub-steps section */}
          {hasSubSteps && isExpanded && (
            <div 
              className={`mt-3 pt-3 space-y-1.5 animate-fade-in ${
                isCritical ? 'border-t border-white/30' : 'border-t border-black/10'
              }`}
            >
              <div className={`text-xs font-semibold mb-2 ${
                isCritical ? 'text-white/90' : 'text-black/60'
              }`}>
                Detailed Steps:
              </div>
              {subSteps.map((step, idx) => (
                <div key={idx} className={`flex items-start gap-2 text-xs ${
                  isCritical ? 'text-white/95' : 'text-black/80'
                }`}>
                  <span className={`flex-shrink-0 font-semibold ${
                    isCritical ? 'text-white/80' : 'text-black/60'
                  }`}>{idx + 1}.</span>
                  <span className="flex-1">{step}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
    </div>
  );
};

export default FlowNode;
