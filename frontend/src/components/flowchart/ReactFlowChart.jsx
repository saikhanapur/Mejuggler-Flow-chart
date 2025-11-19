import React, { useCallback, useMemo, useState, useEffect, useRef } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Panel,
  useNodesState,
  useEdgesState,
  MarkerType,
  Handle,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import ELK from 'elkjs/lib/elk.bundled.js';

const elk = new ELK();

// Automatic layout with ELK - VERTICAL for mobile-friendly display
const getLayoutedElements = async (nodes, edges, direction = 'DOWN') => {
  const graph = {
    id: 'root',
    layoutOptions: {
      'elk.algorithm': 'layered',
      'elk.direction': direction,
      'elk.spacing.nodeNode': '50',  // Tighter spacing
      'elk.layered.spacing.nodeNodeBetweenLayers': '60',  // Compact layers
      'elk.layered.nodePlacement.strategy': 'SIMPLE',
    },
    children: nodes.map((node) => ({
      id: node.id,
      width: 280,  // Slightly wider for better readability
      height: 100,
    })),
    edges: edges.map((edge) => ({
      id: edge.id,
      sources: [edge.source],
      targets: [edge.target],
    })),
  };

  const layoutedGraph = await elk.layout(graph);

  const layoutedNodes = nodes.map((node) => {
    const layoutedNode = layoutedGraph.children?.find((n) => n.id === node.id);
    return {
      ...node,
      position: {
        x: layoutedNode?.x || 0,
        y: layoutedNode?.y || 0,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
};

// Custom node component for process steps
const ProcessNode = ({ data, selected, id }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [expandedHeight, setExpandedHeight] = useState(0);
  const contentRef = React.useRef(null);

  const statusColors = {
    critical: 'bg-red-50 border-red-500',
    trigger: 'bg-blue-50 border-blue-500',
    action: 'bg-green-50 border-green-500',
    communication: 'bg-purple-50 border-purple-500',
    operational: 'bg-emerald-50 border-emerald-500',
    monitoring: 'bg-amber-50 border-amber-500',
    verification: 'bg-teal-50 border-teal-500',
    recovery: 'bg-green-50 border-green-500',
    warning: 'bg-amber-50 border-amber-500',
    decision: 'bg-yellow-50 border-yellow-500',
  };

  const statusBadgeColors = {
    critical: 'bg-red-100 text-red-700 border-red-300',
    trigger: 'bg-blue-100 text-blue-700 border-blue-300',
    action: 'bg-green-100 text-green-700 border-green-300',
    communication: 'bg-purple-100 text-purple-700 border-purple-300',
    operational: 'bg-emerald-100 text-emerald-700 border-emerald-300',
    monitoring: 'bg-amber-100 text-amber-700 border-amber-300',
    verification: 'bg-teal-100 text-teal-700 border-teal-300',
  };

  const colorClass = statusColors[data.type] || statusColors.operational;
  const badgeColor = statusBadgeColors[data.type] || statusBadgeColors.operational;
  
  // Check if we have meaningful details to show
  const hasActions = data.details?.specificActions && data.details.specificActions.length > 0;
  const hasActors = data.details?.actors && data.details.actors.length > 0;
  const hasTimeline = data.details?.timeline;
  const hasPurpose = data.details?.purpose;
  
  const hasQuickInfo = hasActions || hasActors || hasTimeline;

  // Calculate expanded height when dropdown opens
  React.useEffect(() => {
    if (isExpanded && contentRef.current) {
      const height = contentRef.current.offsetHeight;
      setExpandedHeight(height + 20); // Add some padding
      if (data.onExpand) {
        data.onExpand(id, true, height + 20);
      }
    } else if (!isExpanded && data.onExpand) {
      data.onExpand(id, false, 0);
      setExpandedHeight(0);
    }
  }, [isExpanded, id, data]);

  const handleToggle = (e) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  return (
    <>
      <Handle type="target" position={Position.Top} style={{ background: '#64748b', width: 12, height: 12 }} />
      <div
        className={`px-4 py-3 shadow-lg rounded-lg border-2 ${colorClass} w-[280px] transition-all duration-200 hover:shadow-xl cursor-pointer ${
          selected ? 'ring-4 ring-blue-400' : ''
        }`}
      >
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1">
            <div className="font-semibold text-sm text-gray-900">{data.title}</div>
            {data.category && (
              <div className="text-xs text-gray-600 mt-1">{data.category}</div>
            )}
          </div>
          {hasQuickInfo && (
            <button
              onClick={handleToggle}
              className="text-gray-500 hover:text-gray-700 p-1 text-xs flex-shrink-0"
              title="Quick info"
            >
              {isExpanded ? '▲' : '▼'}
            </button>
          )}
        </div>

        {/* ENHANCED DROPDOWN - Quick Abstract View */}
        {isExpanded && hasQuickInfo && (
          <div ref={contentRef} className="mt-3 pt-3 border-t border-gray-200 space-y-2">
            {/* Key Actions - Top 2 only */}
            {hasActions && (
              <div>
                <div className="text-[10px] font-semibold text-gray-500 uppercase tracking-wide mb-1">
                  ⚡ Key Actions
                </div>
                <div className="text-xs text-gray-700 space-y-1">
                  {data.details.specificActions.slice(0, 2).map((action, idx) => (
                    <div key={idx} className="flex items-start gap-1">
                      <span className="text-blue-500 font-bold">•</span>
                      <span className="line-clamp-2">{action}</span>
                    </div>
                  ))}
                  {data.details.specificActions.length > 2 && (
                    <div className="text-[10px] text-gray-500 italic">
                      +{data.details.specificActions.length - 2} more (click node for full details)
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Timeline */}
            {hasTimeline && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-gray-500">⏱️</span>
                <span className="text-gray-700 font-medium">{data.details.timeline}</span>
              </div>
            )}

            {/* Actors */}
            {hasActors && (
              <div className="flex items-start gap-2 text-xs">
                <span className="text-gray-500 flex-shrink-0">👥</span>
                <span className="text-gray-700 line-clamp-1">
                  {data.details.actors.slice(0, 2).join(', ')}
                  {data.details.actors.length > 2 && ` +${data.details.actors.length - 2}`}
                </span>
              </div>
            )}

            {/* Type Badge */}
            <div className="flex items-center justify-between">
              <span className={`text-[10px] px-2 py-0.5 rounded-full border ${badgeColor} font-medium uppercase tracking-wide`}>
                {data.type}
              </span>
              <span className="text-[9px] text-gray-400 italic">
                Click for full details →
              </span>
            </div>
          </div>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} style={{ background: '#64748b', width: 12, height: 12 }} />
    </>
  );
};

// Decision node (diamond shape)
const DecisionNode = ({ data, selected }) => {
  return (
    <>
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      <div className="relative w-32 h-32 flex items-center justify-center">
        <div className={`absolute inset-0 bg-yellow-100 border-2 border-yellow-500 transform rotate-45 shadow-lg ${
          selected ? 'ring-4 ring-blue-400' : ''
        }`}></div>
        <div className="relative z-10 text-center text-xs font-medium text-gray-900 px-2 max-w-[80px]">
          {data.title}
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
    </>
  );
};

const nodeTypes = {
  default: ProcessNode,
  process: ProcessNode,
  decision: DecisionNode,
};

export const ReactFlowChart = ({ processData, onNodeClick }) => {
  const [isLayouting, setIsLayouting] = useState(true);
  const [layoutDirection, setLayoutDirection] = useState('DOWN');
  const [expandedNodeId, setExpandedNodeId] = useState(null);
  const [baseNodePositions, setBaseNodePositions] = useState([]);

  // Convert backend data structure to ReactFlow format
  const initialNodes = useMemo(() => {
    if (!processData?.nodes) return [];

    return processData.nodes.map((node) => {
      const nodeType = node.type === 'decision' ? 'decision' : 'process';

      return {
        id: node.id,
        type: nodeType,
        position: { x: 0, y: 0 },
        data: {
          title: node.title,
          type: node.type,
          category: node.category,
          details: node.operationalDetails || node.details || {},
          originalNode: node,
          onExpand: null, // Will be set after layout
        },
      };
    });
  }, [processData]);

  const initialEdges = useMemo(() => {
    if (!processData?.edges) return [];

    return processData.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label || '',
      type: 'smoothstep',
      animated: true,
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 20,
        height: 20,
        color: '#64748b',
      },
      style: {
        strokeWidth: 2,
        stroke: '#64748b',
      },
    }));
  }, [processData]);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Apply automatic layout - respects direction
  useEffect(() => {
    const applyLayout = async () => {
      if (initialNodes.length > 0) {
        setIsLayouting(true);
        const { nodes: layoutedNodes, edges: layoutedEdges } = await getLayoutedElements(
          initialNodes,
          initialEdges,
          layoutDirection
        );
        
        // Inject onExpand callback into each node's data
        const nodesWithCallbacks = layoutedNodes.map(node => ({
          ...node,
          data: {
            ...node.data,
            onExpand: handleNodeExpand,
          },
        }));
        
        setNodes(nodesWithCallbacks);
        setEdges(layoutedEdges);
        setBaseNodePositions(layoutedNodes.map(n => ({ id: n.id, position: n.position })));
        setExpandedNodeId(null); // Reset expansion on layout change
        setIsLayouting(false);
      }
    };

    applyLayout();
  }, [initialNodes, initialEdges, layoutDirection, handleNodeExpand]);

  const handleNodeClick = useCallback((event, node) => {
    if (onNodeClick) {
      onNodeClick(node.data.originalNode);
    }
  }, [onNodeClick]);

  // Smart layout adjustment when node expands/collapses
  const handleNodeExpand = useCallback((nodeId, isExpanded, expandedHeight) => {
    if (layoutDirection !== 'DOWN') return; // Only for vertical layout

    setExpandedNodeId(isExpanded ? nodeId : null);

    setNodes((currentNodes) => {
      const expandedNodeIndex = currentNodes.findIndex(n => n.id === nodeId);
      if (expandedNodeIndex === -1) return currentNodes;

      const expandedNode = currentNodes[expandedNodeIndex];
      const basePosition = baseNodePositions.find(bp => bp.id === nodeId);
      
      if (!basePosition) return currentNodes;

      // Calculate how much space the expanded content needs
      const extraSpace = isExpanded ? expandedHeight : 0;

      // Update all nodes
      return currentNodes.map((node, index) => {
        const nodeBasePos = baseNodePositions.find(bp => bp.id === node.id);
        if (!nodeBasePos) return node;

        // If this node is below the expanded node, push it down
        if (nodeBasePos.position.y > basePosition.position.y) {
          return {
            ...node,
            position: {
              ...node.position,
              y: nodeBasePos.position.y + extraSpace,
            },
            style: {
              ...node.style,
              transition: 'all 0.3s ease-in-out',
            },
          };
        }

        // If this is the expanded node or above it, keep original position
        return {
          ...node,
          position: nodeBasePos.position,
          style: {
            ...node.style,
            transition: 'all 0.3s ease-in-out',
          },
        };
      });
    });
  }, [layoutDirection, baseNodePositions, setNodes]);

  const swimLanes = useMemo(() => {
    if (!processData?.swimLanes) return [];
    return processData.swimLanes;
  }, [processData]);

  // Calculate swim lane boundaries for visual rendering - MUST BE BEFORE EARLY RETURN
  const swimLaneBoundaries = useMemo(() => {
    if (!swimLanes || swimLanes.length === 0 || nodes.length === 0) return [];

    return swimLanes.map((lane, index) => {
      // Find nodes assigned to this lane
      const laneNodes = nodes.filter(n => lane.nodeIds?.includes(n.id));
      
      if (laneNodes.length === 0) return null;

      // Calculate boundaries based on layout direction
      if (layoutDirection === 'DOWN') {
        // For vertical layout: horizontal bands (top to bottom)
        const minY = Math.min(...laneNodes.map(n => n.position.y)) - 60;
        const maxY = Math.max(...laneNodes.map(n => n.position.y)) + 160;
        
        return {
          id: lane.id,
          name: lane.name || `Phase ${index + 1}`,
          x: -5000, // Extend far left
          y: minY,
          width: 10000, // Extend far right
          height: maxY - minY,
          index,
        };
      } else {
        // For horizontal layout: vertical columns (left to right)
        const minX = Math.min(...laneNodes.map(n => n.position.x)) - 60;
        const maxX = Math.max(...laneNodes.map(n => n.position.x)) + 340;
        
        return {
          id: lane.id,
          name: lane.name || `Phase ${index + 1}`,
          x: minX,
          y: -5000,
          width: maxX - minX,
          height: 10000,
          index,
        };
      }
    }).filter(Boolean);
  }, [swimLanes, nodes, layoutDirection]);

  // Accessible color palette for swim lanes
  const laneColorPalette = [
    { bg: 'rgba(239, 246, 255, 0.7)', border: '#93c5fd', text: '#1e40af' }, // Blue
    { bg: 'rgba(240, 253, 244, 0.7)', border: '#86efac', text: '#166534' }, // Green
    { bg: 'rgba(254, 243, 199, 0.7)', border: '#fde047', text: '#854d0e' }, // Yellow
    { bg: 'rgba(253, 242, 248, 0.7)', border: '#f9a8d4', text: '#9f1239' }, // Pink
    { bg: 'rgba(243, 232, 255, 0.7)', border: '#d8b4fe', text: '#6b21a8' }, // Purple
    { bg: 'rgba(254, 226, 226, 0.7)', border: '#fca5a5', text: '#991b1b' }, // Red
  ];

  // Early return AFTER all hooks
  if (isLayouting) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <div className="text-sm text-gray-600">Optimizing layout...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-gray-50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.3}
        maxZoom={1.5}
        fitViewOptions={{ 
          padding: 0.15,
          includeHiddenNodes: false,
          minZoom: 0.5,
          maxZoom: 1,
        }}
        proOptions={{ hideAttribution: true }}
      >
        {/* Swim Lane Backgrounds - Rendered BEHIND nodes */}
        {swimLaneBoundaries.length > 0 && (
          <svg 
            className="react-flow__swimlanes" 
            style={{ 
              position: 'absolute', 
              top: 0, 
              left: 0, 
              width: '100%', 
              height: '100%', 
              pointerEvents: 'none',
              zIndex: 0,
            }}
          >
            <defs>
              {/* Gradient definitions for subtle depth */}
              {swimLaneBoundaries.map((lane, idx) => {
                const colors = laneColorPalette[idx % laneColorPalette.length];
                return (
                  <linearGradient 
                    key={`gradient-${lane.id}`} 
                    id={`gradient-${lane.id}`} 
                    x1="0%" 
                    y1="0%" 
                    x2="0%" 
                    y2="100%"
                  >
                    <stop offset="0%" style={{ stopColor: colors.bg, stopOpacity: 0.9 }} />
                    <stop offset="100%" style={{ stopColor: colors.bg, stopOpacity: 0.7 }} />
                  </linearGradient>
                );
              })}
            </defs>

            {swimLaneBoundaries.map((lane, idx) => {
              const colors = laneColorPalette[idx % laneColorPalette.length];
              
              return (
                <g key={lane.id}>
                  {/* Lane background with gradient */}
                  <rect
                    x={lane.x}
                    y={lane.y}
                    width={lane.width}
                    height={lane.height}
                    fill={`url(#gradient-${lane.id})`}
                    stroke={colors.border}
                    strokeWidth="2"
                    strokeDasharray={layoutDirection === 'DOWN' ? '8,4' : '8,4'}
                    rx="8"
                  />
                  
                  {/* Lane label */}
                  <text
                    x={layoutDirection === 'DOWN' ? 40 : lane.x + lane.width / 2}
                    y={layoutDirection === 'DOWN' ? lane.y + 35 : -4800}
                    fill={colors.text}
                    fontSize="16"
                    fontWeight="700"
                    textAnchor={layoutDirection === 'DOWN' ? 'start' : 'middle'}
                  >
                    {lane.name}
                  </text>
                  
                  {/* Subtle phase number badge */}
                  <circle
                    cx={layoutDirection === 'DOWN' ? 20 : lane.x + 20}
                    cy={layoutDirection === 'DOWN' ? lane.y + 30 : -4800}
                    r="12"
                    fill={colors.border}
                    opacity="0.8"
                  />
                  <text
                    x={layoutDirection === 'DOWN' ? 20 : lane.x + 20}
                    y={layoutDirection === 'DOWN' ? lane.y + 35 : -4795}
                    fill="white"
                    fontSize="11"
                    fontWeight="700"
                    textAnchor="middle"
                  >
                    {idx + 1}
                  </text>
                </g>
              );
            })}
          </svg>
        )}

        <Background color="#cbd5e1" gap={20} size={1} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            const colors = {
              critical: '#fca5a5',
              trigger: '#93c5fd',
              action: '#86efac',
              decision: '#fde047',
              operational: '#6ee7b7',
            };
            return colors[node.data.type] || '#d1d5db';
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
          style={{ background: 'white' }}
        />

        <Panel position="top-left" className="bg-white p-3 rounded-lg shadow-lg border border-gray-200 max-w-xs">
          <div className="text-sm font-bold text-gray-900">
            {processData?.name || 'Process Flowchart'}
          </div>
          {processData?.description && (
            <div className="text-xs text-gray-600 mt-1">
              {processData.description}
            </div>
          )}
          <div className="text-xs text-gray-500 mt-2 flex items-center gap-2">
            <span>{nodes.length} steps</span>
            <span>•</span>
            <span>{swimLanes.length} phases</span>
          </div>

          {/* Swim Lane Legend */}
          {swimLaneBoundaries.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="text-xs font-semibold text-gray-700 mb-2">🏊 Process Phases:</div>
              <div className="space-y-1.5">
                {swimLaneBoundaries.map((lane, idx) => {
                  const colors = laneColorPalette[idx % laneColorPalette.length];
                  return (
                    <div key={lane.id} className="flex items-center gap-2">
                      <div 
                        className="w-6 h-6 rounded flex items-center justify-center text-white text-[10px] font-bold"
                        style={{ backgroundColor: colors.border }}
                      >
                        {idx + 1}
                      </div>
                      <span className="text-xs text-gray-700 font-medium">
                        {lane.name}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="text-xs text-gray-600 mb-2">Layout:</div>
            <div className="flex gap-2">
              <button
                onClick={() => setLayoutDirection('DOWN')}
                className={`px-3 py-1.5 text-xs rounded transition-colors ${
                  layoutDirection === 'DOWN'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                📱 Vertical
              </button>
              <button
                onClick={() => setLayoutDirection('RIGHT')}
                className={`px-3 py-1.5 text-xs rounded transition-colors ${
                  layoutDirection === 'RIGHT'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                🖥️ Horizontal
              </button>
            </div>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
};
