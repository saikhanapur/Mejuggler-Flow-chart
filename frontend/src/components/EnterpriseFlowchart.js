import React, { useCallback, useMemo, useState, useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  Panel
} from 'reactflow';
import 'reactflow/dist/style.css';
import { ChevronDown, ChevronRight, Maximize2, Minimize2 } from 'lucide-react';
import dagre from 'dagre';

// Custom Node Components
const ActionNode = ({ data }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'trigger': return 'from-blue-500 to-indigo-600';
      case 'current': return 'from-purple-500 to-pink-600';
      case 'warning': return 'from-yellow-500 to-orange-600';
      case 'critical-gap': return 'from-red-500 to-rose-600';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  const hasDetails = data.operationalDetails && (
    data.operationalDetails.specificActions?.length > 0 ||
    data.operationalDetails.contactInfo && Object.keys(data.operationalDetails.contactInfo).length > 0 ||
    data.operationalDetails.systems?.length > 0
  );

  return (
    <div 
      className={`px-4 py-3 rounded-lg shadow-md border-2 border-gray-200 bg-gradient-to-r ${getStatusColor(data.status)} text-white min-w-[200px] max-w-[280px] cursor-pointer hover:shadow-lg transition-all`}
      onClick={() => data.onNodeClick?.(data)}
    >
      <div className="font-semibold text-sm mb-1">{data.title}</div>
      {data.description && (
        <div className="text-xs opacity-90 mb-2">{data.description}</div>
      )}
      {data.subSteps && data.subSteps.length > 0 && (
        <div className="text-xs opacity-80 mt-2">
          {data.subSteps.length} sub-steps
        </div>
      )}
      {hasDetails && (
        <div className="mt-2 text-xs bg-white/20 px-2 py-1 rounded">
          Click for details
        </div>
      )}
    </div>
  );
};

const DecisionNode = ({ data }) => {
  return (
    <div className="relative">
      {/* Diamond shape using CSS transform */}
      <div 
        className="w-40 h-40 bg-gradient-to-br from-yellow-400 to-orange-500 transform rotate-45 shadow-lg cursor-pointer hover:shadow-xl transition-all border-2 border-gray-200"
        onClick={() => data.onNodeClick?.(data)}
      >
        {/* Content rotated back */}
        <div className="absolute inset-0 flex items-center justify-center transform -rotate-45">
          <div className="text-white font-semibold text-sm text-center px-4">
            {data.title}
          </div>
        </div>
      </div>
    </div>
  );
};

const GroupNode = ({ data }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="px-5 py-4 rounded-xl shadow-lg border-2 border-indigo-300 bg-gradient-to-br from-indigo-50 to-purple-50 min-w-[300px]">
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div>
          <div className="font-bold text-indigo-900 text-base">{data.title}</div>
          <div className="text-sm text-indigo-600">
            {data.nodeCount} steps
          </div>
        </div>
        {isExpanded ? (
          <ChevronDown className="w-5 h-5 text-indigo-600" />
        ) : (
          <ChevronRight className="w-5 h-5 text-indigo-600" />
        )}
      </div>
      {isExpanded && data.description && (
        <div className="mt-3 text-sm text-gray-700">{data.description}</div>
      )}
    </div>
  );
};

// Node type mapping
const nodeTypes = {
  action: ActionNode,
  decision: DecisionNode,
  group: GroupNode,
};

// Auto-layout using dagre
const getLayoutedElements = (nodes, edges, swimLanes = []) => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  
  const nodeWidth = 250;
  const nodeHeight = 100;
  const rankSep = 150; // Horizontal spacing
  const nodeSep = 100;  // Vertical spacing between swim lanes

  dagreGraph.setGraph({ 
    rankdir: 'LR', // Left to right
    ranksep: rankSep,
    nodesep: nodeSep,
    marginx: 50,
    marginy: 50
  });

  // Add nodes to dagre
  nodes.forEach((node) => {
    const width = node.type === 'decision' ? 160 : nodeWidth;
    const height = node.type === 'decision' ? 160 : nodeHeight;
    dagreGraph.setNode(node.id, { width, height });
  });

  // Add edges to dagre
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  // Apply swim lane offsets
  const laneHeight = 200;
  const laneMap = {};
  swimLanes.forEach((lane, index) => {
    laneMap[lane.id] = index * laneHeight;
  });

  // Position nodes
  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    const swimLaneOffset = laneMap[node.data.swimLane] || 0;
    
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - nodeWithPosition.width / 2,
        y: nodeWithPosition.y - nodeWithPosition.height / 2 + swimLaneOffset,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
};

const EnterpriseFlowchart = ({ process, onNodeClick }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Transform process data to React Flow format
  useEffect(() => {
    if (!process || !process.nodes) return;

    const swimLanes = process.swimLanes || [];
    
    // Create nodes
    const flowNodes = process.nodes.map((node) => {
      let nodeType = 'action';
      if (node.type === 'decision') {
        nodeType = 'decision';
      }

      return {
        id: node.id,
        type: nodeType,
        data: {
          ...node,
          swimLane: node.swimLane,
          onNodeClick: handleNodeClick,
        },
        position: node.position || { x: 0, y: 0 },
      };
    });

    // Create edges with styling
    const flowEdges = (process.edges || []).map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      type: 'smoothstep',
      animated: edge.condition === 'yes',
      style: {
        stroke: edge.condition === 'yes' ? '#10b981' : edge.condition === 'no' ? '#ef4444' : '#6366f1',
        strokeWidth: 2,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: edge.condition === 'yes' ? '#10b981' : edge.condition === 'no' ? '#ef4444' : '#6366f1',
      },
      labelStyle: {
        fill: edge.condition === 'yes' ? '#10b981' : edge.condition === 'no' ? '#ef4444' : '#6366f1',
        fontWeight: 600,
        fontSize: 12,
      },
      labelBgStyle: {
        fill: '#ffffff',
        fillOpacity: 0.9,
      },
    }));

    // Auto-layout
    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
      flowNodes,
      flowEdges,
      swimLanes
    );

    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
  }, [process]);

  const handleNodeClick = useCallback((nodeData) => {
    setSelectedNode(nodeData);
    if (onNodeClick) {
      onNodeClick(nodeData);
    }
  }, [onNodeClick]);

  // Swim lane backgrounds
  const swimLaneBackgrounds = useMemo(() => {
    if (!process?.swimLanes || process.swimLanes.length === 0) return null;

    return process.swimLanes.map((lane, index) => (
      <div
        key={lane.id}
        className="absolute left-0 right-0 border-b border-gray-200"
        style={{
          top: index * 200,
          height: 200,
          backgroundColor: index % 2 === 0 ? '#f9fafb' : '#ffffff',
          zIndex: -1,
        }}
      >
        <div className="absolute left-4 top-4">
          <div className="font-bold text-gray-700 text-sm">{lane.name}</div>
          {lane.role && (
            <div className="text-xs text-gray-500">{lane.role}</div>
          )}
        </div>
      </div>
    ));
  }, [process?.swimLanes]);

  return (
    <div className={`${isFullscreen ? 'fixed inset-0 z-50 bg-white' : 'relative'} h-full w-full`}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.1}
        maxZoom={2}
        defaultEdgeOptions={{
          type: 'smoothstep',
        }}
      >
        <Background color="#e5e7eb" gap={16} />
        <Controls />
        <MiniMap 
          nodeColor={(node) => {
            if (node.type === 'decision') return '#fbbf24';
            return '#6366f1';
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
        
        {/* Swim lane labels */}
        {swimLaneBackgrounds && (
          <div className="absolute inset-0 pointer-events-none">
            {swimLaneBackgrounds}
          </div>
        )}

        {/* Fullscreen toggle */}
        <Panel position="top-right" className="bg-white p-2 rounded-lg shadow-md">
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-2 hover:bg-gray-100 rounded transition-colors"
          >
            {isFullscreen ? (
              <Minimize2 className="w-5 h-5 text-gray-700" />
            ) : (
              <Maximize2 className="w-5 h-5 text-gray-700" />
            )}
          </button>
        </Panel>

        {/* Process info */}
        <Panel position="top-left" className="bg-white p-4 rounded-lg shadow-md max-w-md">
          <div className="font-bold text-gray-900">{process?.name || 'Process Flow'}</div>
          <div className="text-sm text-gray-600 mt-1">
            {process?.nodes?.length || 0} steps · {process?.edges?.length || 0} connections
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
};

export default EnterpriseFlowchart;
