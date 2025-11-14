import React, { useCallback, useMemo, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Panel,
  useNodesState,
  useEdgesState,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// Custom node component for process steps
const ProcessNode = ({ data }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const statusColors = {
    critical: 'bg-red-50 border-red-400',
    trigger: 'bg-blue-50 border-blue-400',
    action: 'bg-green-50 border-green-400',
    communication: 'bg-purple-50 border-purple-400',
    operational: 'bg-emerald-50 border-emerald-400',
    monitoring: 'bg-amber-50 border-amber-400',
    verification: 'bg-teal-50 border-teal-400',
    recovery: 'bg-green-50 border-green-400',
    warning: 'bg-amber-50 border-amber-400',
    decision: 'bg-yellow-50 border-yellow-400',
  };

  const colorClass = statusColors[data.type] || statusColors.operational;
  const hasDetails = data.details?.specificActions && data.details.specificActions.length > 0;

  return (
    <div
      className={`px-4 py-3 shadow-md rounded-lg border-2 ${colorClass} min-w-[250px] transition-all duration-200 hover:shadow-lg`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <div className="font-semibold text-sm text-gray-900">{data.title}</div>
          {data.category && (
            <div className="text-xs text-gray-600 mt-1">{data.category}</div>
          )}
        </div>
        {hasDetails && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-gray-500 hover:text-gray-700 p-1"
          >
            {isExpanded ? '▲' : '▼'}
          </button>
        )}
      </div>

      {isExpanded && hasDetails && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="text-xs text-gray-700 space-y-1">
            {data.details.specificActions.slice(0, 3).map((action, idx) => (
              <div key={idx} className="flex items-start gap-1">
                <span className="text-gray-400">•</span>
                <span>{action}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Decision node (diamond shape)
const DecisionNode = ({ data }) => {
  return (
    <div className="relative w-32 h-32 flex items-center justify-center">
      <div className="absolute inset-0 bg-yellow-100 border-2 border-yellow-400 transform rotate-45 shadow-md"></div>
      <div className="relative z-10 text-center text-xs font-medium text-gray-900 px-2 max-w-[80px]">
        {data.title}
      </div>
    </div>
  );
};

const nodeTypes = {
  default: ProcessNode,
  process: ProcessNode,
  decision: DecisionNode,
};

export const ReactFlowChart = ({ processData }) => {
  // Convert backend data structure to ReactFlow format
  const initialNodes = useMemo(() => {
    if (!processData?.nodes) return [];

    return processData.nodes.map((node) => {
      // Determine node type
      const nodeType = node.type === 'decision' ? 'decision' : 'process';

      return {
        id: node.id,
        type: nodeType,
        position: node.position || { x: 0, y: 0 },
        data: {
          title: node.title,
          type: node.type,
          category: node.category,
          details: node.operationalDetails || node.details || {},
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
      type: edge.style === 'dashed' ? 'step' : 'smoothstep',
      animated: edge.style !== 'dashed',
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 20,
        height: 20,
      },
      style: {
        strokeWidth: 2,
        stroke: '#94a3b8',
      },
    }));
  }, [processData]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Create swim lane backgrounds
  const swimLanes = useMemo(() => {
    if (!processData?.swimLanes) return [];
    return processData.swimLanes;
  }, [processData]);

  return (
    <div className="w-full h-full bg-gray-50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.1}
        maxZoom={2}
        defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
        proOptions={{ hideAttribution: true }}
      >
        {/* Swim lane backgrounds */}
        {swimLanes.length > 0 && (
          <svg className="react-flow__swimlanes" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
            {swimLanes.map((lane, index) => {
              // Calculate lane position based on nodes assigned to it
              const laneNodes = nodes.filter(n => lane.nodeIds?.includes(n.id));
              if (laneNodes.length === 0) return null;

              const minY = Math.min(...laneNodes.map(n => n.position.y)) - 80;
              const maxY = Math.max(...laneNodes.map(n => n.position.y + 150)) + 80;
              const height = maxY - minY;

              const colors = [
                'rgba(239, 246, 255, 0.6)',  // blue
                'rgba(240, 253, 244, 0.6)',  // green
                'rgba(254, 252, 232, 0.6)',  // yellow
                'rgba(253, 242, 248, 0.6)',  // pink
              ];

              return (
                <g key={lane.id}>
                  <rect
                    x="-10000"
                    y={minY}
                    width="20000"
                    height={height}
                    fill={colors[index % colors.length]}
                    stroke="#cbd5e1"
                    strokeWidth="1"
                  />
                  <text
                    x="20"
                    y={minY + 30}
                    fill="#475569"
                    fontSize="14"
                    fontWeight="600"
                  >
                    {lane.name || `Lane ${index + 1}`}
                  </text>
                </g>
              );
            })}
          </svg>
        )}

        <Background color="#e2e8f0" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            const colors = {
              critical: '#fecaca',
              trigger: '#bfdbfe',
              action: '#bbf7d0',
              decision: '#fef08a',
            };
            return colors[node.data.type] || '#d1d5db';
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />

        <Panel position="top-left" className="bg-white p-3 rounded-lg shadow-md">
          <div className="text-sm font-semibold text-gray-900">
            {processData?.name || 'Process Flowchart'}
          </div>
          {processData?.description && (
            <div className="text-xs text-gray-600 mt-1">
              {processData.description}
            </div>
          )}
          <div className="text-xs text-gray-500 mt-2">
            {nodes.length} steps • {swimLanes.length} phases
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
};
