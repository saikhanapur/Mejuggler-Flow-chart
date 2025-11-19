import React, { useCallback, useMemo, useState, useEffect } from 'react';
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
const ProcessNode = ({ data, selected }) => {
  const [isExpanded, setIsExpanded] = useState(false);

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
              onClick={(e) => {
                e.stopPropagation();
                setIsExpanded(!isExpanded);
              }}
              className="text-gray-500 hover:text-gray-700 p-1 text-xs flex-shrink-0"
              title="Quick info"
            >
              {isExpanded ? '▲' : '▼'}
            </button>
          )}
        </div>

        {/* ENHANCED DROPDOWN - Quick Abstract View */}
        {isExpanded && hasQuickInfo && (
          <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
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
        setNodes(layoutedNodes);
        setEdges(layoutedEdges);
        setIsLayouting(false);
      }
    };

    applyLayout();
  }, [initialNodes, initialEdges, layoutDirection]);

  const handleNodeClick = useCallback((event, node) => {
    if (onNodeClick) {
      onNodeClick(node.data.originalNode);
    }
  }, [onNodeClick]);

  const swimLanes = useMemo(() => {
    if (!processData?.swimLanes) return [];
    return processData.swimLanes;
  }, [processData]);

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

        <Panel position="top-left" className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <div className="text-sm font-bold text-gray-900">
            {processData?.name || 'Process Flowchart'}
          </div>
          {processData?.description && (
            <div className="text-xs text-gray-600 mt-1 max-w-xs">
              {processData.description}
            </div>
          )}
          <div className="text-xs text-gray-500 mt-2 flex items-center gap-2">
            <span>{nodes.length} steps</span>
            <span>•</span>
            <span>{swimLanes.length} phases</span>
          </div>
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
