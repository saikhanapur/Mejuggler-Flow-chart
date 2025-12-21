/**
 * CLEAN FLOWCHART LAYOUT - Enterprise Grade
 * 
 * Design Principles (what a top engineer would do):
 * 1. CONSISTENT FLOW: Always top-to-bottom
 * 2. DECISION RULES: YES always left/down (green), NO always right/down (red)
 * 3. SOLID LINES: No dotted/animated noise - clear, solid connections
 * 4. VISUAL HIERARCHY: Decision nodes are prominent, branches are color-coded
 * 5. MINIMAL CROSSINGS: Smart port allocation to prevent edge crossing
 */

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
import { toast } from 'sonner';

const elk = new ELK();

/**
 * CLEAN LAYOUT ALGORITHM
 * 
 * Key improvements:
 * 1. Enforce strict top-to-bottom flow
 * 2. Decision nodes have dedicated YES (left) and NO (right) ports
 * 3. Larger spacing to prevent overlap
 * 4. Orthogonal edge routing for clean lines
 */
const getCleanLayoutedElements = async (nodes, edges, direction = 'DOWN') => {
  console.log('🎨 Clean layout starting', { nodesCount: nodes.length, edgesCount: edges.length });
  
  try {
    const validNodeIds = new Set(nodes.map(n => n.id));
    const validEdges = edges.filter(edge => 
      validNodeIds.has(edge.source) && validNodeIds.has(edge.target)
    );

    // Identify decision nodes for special port handling
    const decisionNodeIds = new Set(
      nodes.filter(n => n.type === 'decision').map(n => n.id)
    );

    const graph = {
      id: 'root',
      layoutOptions: {
        'elk.algorithm': 'layered',
        'elk.direction': direction,
        
        // GENEROUS SPACING - prevents overlap
        'elk.spacing.nodeNode': '100',
        'elk.layered.spacing.nodeNodeBetweenLayers': '120',
        'elk.spacing.edgeNode': '50',
        'elk.spacing.edgeEdge': '30',
        
        // CLEAN EDGE ROUTING
        'elk.edgeRouting': 'ORTHOGONAL',
        'elk.layered.unnecessaryBendpoints': 'true',
        
        // MINIMIZE CROSSINGS - critical for clarity
        'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',
        'elk.layered.crossingMinimization.greedySwitch.type': 'TWO_SIDED',
        
        // BALANCED NODE PLACEMENT
        'elk.layered.nodePlacement.strategy': 'NETWORK_SIMPLEX',
        'elk.layered.nodePlacement.bk.fixedAlignment': 'BALANCED',
        
        // CONSISTENT ORDERING
        'elk.layered.considerModelOrder.strategy': 'PREFER_NODES',
        
        // PORT CONSTRAINTS for decision branches
        'elk.portConstraints': 'FIXED_ORDER',
      },
      children: nodes.map((node) => {
        const isDecision = node.type === 'decision';
        
        // Decision nodes need specific ports for YES/NO branches
        const ports = isDecision ? [
          { id: `${node.id}_in`, properties: { 'port.side': 'NORTH' } },
          { id: `${node.id}_yes`, properties: { 'port.side': 'WEST' } },  // YES goes left
          { id: `${node.id}_no`, properties: { 'port.side': 'EAST' } },   // NO goes right
          { id: `${node.id}_out`, properties: { 'port.side': 'SOUTH' } }, // Default out
        ] : [
          { id: `${node.id}_in`, properties: { 'port.side': 'NORTH' } },
          { id: `${node.id}_out`, properties: { 'port.side': 'SOUTH' } },
        ];
        
        return {
          id: node.id,
          width: isDecision ? 180 : 280,
          height: isDecision ? 120 : 80,
          ports: ports,
          properties: {
            'portConstraints': 'FIXED_SIDE',
          },
        };
      }),
      edges: validEdges.map((edge) => {
        // Determine source port based on edge type
        let sourcePort = `${edge.source}_out`;
        if (decisionNodeIds.has(edge.source)) {
          if (edge.label?.includes('YES') || edge.isYesBranch) {
            sourcePort = `${edge.source}_yes`;
          } else if (edge.label?.includes('NO') || edge.isNoBranch) {
            sourcePort = `${edge.source}_no`;
          }
        }
        
        return {
          id: edge.id,
          sources: [sourcePort],
          targets: [`${edge.target}_in`],
        };
      }),
    };

    const layoutedGraph = await elk.layout(graph);
    console.log('✅ Clean layout complete');

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

    return { nodes: layoutedNodes, edges: validEdges };
  } catch (error) {
    console.error('❌ Layout Error:', error);
    // Simple fallback
    const fallbackNodes = nodes.map((node, index) => ({
      ...node,
      position: { x: 200, y: index * 150 },
    }));
    return { nodes: fallbackNodes, edges };
  }
};


/**
 * CLEAN PROCESS NODE
 * - Solid border, clear background
 * - No excessive decoration
 * - Clear title and optional details
 */
const CleanProcessNode = ({ data, selected, id }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const contentRef = useRef(null);
  
  // Simple, clear color coding by type
  const typeColors = {
    critical: { bg: '#fef2f2', border: '#dc2626', text: '#991b1b' },
    trigger: { bg: '#eff6ff', border: '#2563eb', text: '#1e40af' },
    action: { bg: '#f0fdf4', border: '#16a34a', text: '#166534' },
    communication: { bg: '#faf5ff', border: '#9333ea', text: '#7e22ce' },
    operational: { bg: '#f0fdfa', border: '#14b8a6', text: '#0f766e' },
    monitoring: { bg: '#fffbeb', border: '#f59e0b', text: '#b45309' },
    default: { bg: '#f8fafc', border: '#64748b', text: '#334155' },
  };
  
  const colors = typeColors[data.type] || typeColors.default;
  
  const hasDetails = data.details?.specificActions?.length > 0 || 
                     data.details?.actors?.length > 0 ||
                     data.details?.timeline;

  return (
    <>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ 
          background: colors.border,
          width: 10,
          height: 10,
          border: '2px solid white',
        }} 
      />
      
      <div
        className={`
          w-[260px] rounded-lg shadow-md transition-all duration-200
          ${selected ? 'ring-2 ring-blue-500 ring-offset-2' : ''}
        `}
        style={{
          backgroundColor: colors.bg,
          border: `2px solid ${colors.border}`,
        }}
      >
        {/* Header */}
        <div className="px-4 py-3">
          <div className="flex items-start justify-between gap-2">
            <h3 
              className="font-semibold text-sm leading-tight"
              style={{ color: colors.text }}
            >
              {data.title}
            </h3>
            {hasDetails && (
              <button
                onClick={(e) => { e.stopPropagation(); setIsExpanded(!isExpanded); }}
                className="text-xs px-2 py-0.5 rounded bg-white/50 hover:bg-white/80 transition-colors"
                style={{ color: colors.text }}
              >
                {isExpanded ? '−' : '+'}
              </button>
            )}
          </div>
          
          {/* Type badge */}
          <span 
            className="inline-block mt-2 text-[10px] px-2 py-0.5 rounded-full font-medium uppercase tracking-wide"
            style={{ 
              backgroundColor: `${colors.border}20`,
              color: colors.text,
            }}
          >
            {data.type || 'action'}
          </span>
        </div>
        
        {/* Expandable details */}
        {isExpanded && hasDetails && (
          <div 
            ref={contentRef}
            className="px-4 pb-3 pt-2 border-t text-xs space-y-2"
            style={{ borderColor: `${colors.border}40` }}
          >
            {data.details?.specificActions?.slice(0, 3).map((action, i) => (
              <div key={i} className="flex gap-2">
                <span style={{ color: colors.border }}>•</span>
                <span className="text-gray-700">{action}</span>
              </div>
            ))}
            {data.details?.timeline && (
              <div className="flex gap-2 text-gray-600">
                <span>⏱</span>
                <span>{data.details.timeline}</span>
              </div>
            )}
          </div>
        )}
      </div>
      
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ 
          background: colors.border,
          width: 10,
          height: 10,
          border: '2px solid white',
        }} 
      />
    </>
  );
};


/**
 * CLEAN DECISION NODE
 * - Clear diamond shape
 * - Prominent YES/NO labels ATTACHED to the node (not on edges)
 * - Green left port for YES, Red right port for NO
 */
const CleanDecisionNode = ({ data, selected }) => {
  return (
    <div className="relative">
      {/* Input handle - top */}
      <Handle 
        type="target" 
        position={Position.Top}
        style={{ 
          background: '#f59e0b',
          width: 12,
          height: 12,
          border: '3px solid white',
          top: -6,
          left: '50%',
          transform: 'translateX(-50%)',
        }} 
      />
      
      {/* YES label - left side */}
      <div 
        className="absolute -left-16 top-1/2 -translate-y-1/2 flex items-center gap-1"
        style={{ zIndex: 10 }}
      >
        <span className="text-xs font-bold text-white bg-green-500 px-2 py-1 rounded shadow">
          YES ✓
        </span>
        <div className="w-4 h-0.5 bg-green-500"></div>
      </div>
      
      {/* NO label - right side */}
      <div 
        className="absolute -right-14 top-1/2 -translate-y-1/2 flex items-center gap-1"
        style={{ zIndex: 10 }}
      >
        <div className="w-4 h-0.5 bg-red-500"></div>
        <span className="text-xs font-bold text-white bg-red-500 px-2 py-1 rounded shadow">
          NO ✗
        </span>
      </div>
      
      {/* Diamond shape */}
      <div 
        className={`
          w-[140px] h-[140px] flex items-center justify-center
          ${selected ? 'ring-4 ring-blue-500 ring-offset-4' : ''}
        `}
      >
        {/* Diamond background */}
        <div 
          className="absolute w-[100px] h-[100px] rotate-45 shadow-lg"
          style={{
            background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 50%, #fbbf24 100%)',
            border: '3px solid #f59e0b',
          }}
        />
        
        {/* Question icon */}
        <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-6 h-6 bg-amber-500 rounded-full flex items-center justify-center shadow">
          <span className="text-white text-xs font-bold">?</span>
        </div>
        
        {/* Text */}
        <div className="relative z-10 text-center px-2 max-w-[90px]">
          <span className="text-xs font-semibold text-amber-900 leading-tight">
            {data.title}
          </span>
        </div>
      </div>
      
      {/* YES output handle - left */}
      <Handle 
        type="source" 
        position={Position.Left}
        id="yes"
        style={{ 
          background: '#22c55e',
          width: 12,
          height: 12,
          border: '3px solid white',
          left: 14,
        }} 
      />
      
      {/* NO output handle - right */}
      <Handle 
        type="source" 
        position={Position.Right}
        id="no"
        style={{ 
          background: '#ef4444',
          width: 12,
          height: 12,
          border: '3px solid white',
          right: 14,
        }} 
      />
      
      {/* Default output handle - bottom (for non-decision connections) */}
      <Handle 
        type="source" 
        position={Position.Bottom}
        id="default"
        style={{ 
          background: '#f59e0b',
          width: 10,
          height: 10,
          border: '2px solid white',
          bottom: -5,
        }} 
      />
    </div>
  );
};


const cleanNodeTypes = {
  default: CleanProcessNode,
  process: CleanProcessNode,
  decision: CleanDecisionNode,
};


/**
 * CREATE CLEAN EDGES
 * - SOLID lines (not dotted) for clarity
 * - GREEN for YES branches
 * - RED for NO branches
 * - GRAY for regular connections
 */
const createCleanEdges = (nodes, edges, decisionNodesMap) => {
  return edges.map((edge) => {
    let edgeLabel = '';
    let edgeColor = '#64748b'; // Default gray
    let sourceHandle = undefined;
    let isYesBranch = false;
    let isNoBranch = false;
    
    // Check if this edge comes from a decision node
    if (decisionNodesMap.has(edge.source)) {
      const decisionOptions = decisionNodesMap.get(edge.source);
      
      if (decisionOptions.yes === edge.target) {
        edgeColor = '#22c55e'; // Green
        sourceHandle = 'yes';
        isYesBranch = true;
        // Don't add label - it's on the node now
      } else if (decisionOptions.no === edge.target) {
        edgeColor = '#ef4444'; // Red
        sourceHandle = 'no';
        isNoBranch = true;
        // Don't add label - it's on the node now
      }
    }
    
    return {
      id: edge.id,
      source: edge.source,
      target: edge.target,
      sourceHandle: sourceHandle,
      label: edgeLabel,
      type: 'smoothstep',
      animated: false, // NO ANIMATION - clean, static lines
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 16,
        height: 16,
        color: edgeColor,
      },
      style: {
        strokeWidth: 2.5,
        stroke: edgeColor,
        // SOLID LINE - no dash array
      },
      labelStyle: {
        fill: edgeColor,
        fontWeight: 700,
        fontSize: 12,
      },
      labelBgStyle: {
        fill: '#ffffff',
        fillOpacity: 0.9,
      },
      labelBgPadding: [8, 4],
      labelBgBorderRadius: 4,
    };
  });
};


export { 
  getCleanLayoutedElements, 
  CleanProcessNode, 
  CleanDecisionNode, 
  cleanNodeTypes,
  createCleanEdges 
};
