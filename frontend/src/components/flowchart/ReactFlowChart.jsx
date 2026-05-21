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

// Automatic layout with ELK - VERTICAL for mobile-friendly display
const getLayoutedElements = async (nodes, edges, direction = 'DOWN') => {
  console.log('🎨 getLayoutedElements called', { nodesCount: nodes.length, edgesCount: edges.length, direction });
  
  try {
    // Validate data before sending to ELK
    const validNodeIds = new Set(nodes.map(n => n.id));
    const validEdges = edges.filter(edge => 
      validNodeIds.has(edge.source) && validNodeIds.has(edge.target)
    );

    if (validEdges.length !== edges.length) {
      console.warn(`⚠️ Filtered ${edges.length - validEdges.length} invalid edges before layout`);
    }

    const graph = {
      id: 'root',
      layoutOptions: {
        'elk.algorithm': 'layered',
        'elk.direction': direction,
        // Spacing configuration for clean, uncluttered layouts
        'elk.spacing.nodeNode': '200',  // Horizontal min spacing between nodes
        'elk.layered.spacing.nodeNodeBetweenLayers': '220',  // Vertical min spacing between layers
        'elk.layered.spacing.edgeNodeBetweenLayers': '60',  // Space between edges and nodes
        'elk.spacing.edgeNode': '40',  // Additional edge-to-node spacing
        'elk.spacing.edgeEdge': '20',  // Space between parallel edges
        
        // Placement and routing for optimal clarity
        'elk.layered.nodePlacement.strategy': 'BRANDES_KOEPF',  // Cleaner branch separation
        'elk.layered.nodePlacement.bk.fixedAlignment': 'BALANCED',  // Balanced alignment
        'elk.edgeRouting': 'POLYLINE',  // Reduces sharp crossing angles
        'elk.layered.unnecessaryBendpoints': 'false',  // Minimize bends
        'elk.layered.considerModelOrder.strategy': 'PREFER_EDGES',  // Optimize for edge clarity
        
        // Decision node handling
        'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',  // Reduce edge crossings
        'elk.layered.cycleBreaking.strategy': 'GREEDY',  // Handle cycles efficiently
        
        // Improve label placement
        'elk.edgeLabels.inline': 'true',  // Keep labels inline with edges
        'elk.edgeLabels.placement': 'TAIL',  // Anchor YES/NO labels at decision node output point
      },
      children: nodes.map((node) => {
        const isDecision = node.type === 'decision';
        const child = {
          id: node.id,
          width: isDecision ? 200 : 280,
          height: isDecision ? 200 : 100,
        };
        if (isDecision) {
          // 60px top/bottom padding so YES and NO branches visually separate before converging
          child.layoutOptions = { 'elk.padding': '[top=60, bottom=60, left=20, right=20]' };
        }
        return child;
      }),
      edges: validEdges.map((edge) => ({
        id: edge.id,
        sources: [edge.source],
        targets: [edge.target],
      })),
    };

    console.log('🔄 Calling ELK layout...');
    const layoutedGraph = await elk.layout(graph);
    console.log('✅ ELK layout returned successfully');

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
    console.error('❌ ELK Layout Error:', error);
    // Fallback: Simple vertical layout without ELK
    const fallbackNodes = nodes.map((node, index) => ({
      ...node,
      position: {
        x: 100,
        y: index * 200,
      },
    }));
    return { nodes: fallbackNodes, edges };
  }
};

// Custom node component for process steps
const ProcessNode = ({ data, selected, id }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [expandedHeight, setExpandedHeight] = useState(0);
  const contentRef = useRef(null);

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
  useEffect(() => {
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

// Decision node (diamond shape) - IMPROVED WITH BETTER SPACING & DESIGN
const DecisionNode = ({ data, selected }) => {
  // Wrap text for better readability
  const wrapText = (text, maxLength = 18) => {
    const words = (text || "Decision").split(' ');
    const lines = [];
    let currentLine = '';
    
    words.forEach(word => {
      if ((currentLine + word).length <= maxLength) {
        currentLine += (currentLine ? ' ' : '') + word;
      } else {
        if (currentLine) lines.push(currentLine);
        currentLine = word;
      }
    });
    if (currentLine) lines.push(currentLine);
    
    // Limit to 3 lines
    return lines.slice(0, 3).map((line, i) => 
      i === 2 && lines.length > 3 ? line.substring(0, 15) + '...' : line
    );
  };
  
  const textLines = wrapText(data.title);
  
  return (
    <>
      {/* Connection handles with better positioning for spacing */}
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ 
          background: '#f59e0b',
          width: 12,
          height: 12,
          border: '2px solid white',
          top: -6
        }} 
      />
      
      {/* Beautiful soft yellow gradient diamond */}
      <div className="relative w-32 h-32 flex items-center justify-center">
        <div 
          className={`absolute inset-0 transform rotate-45 shadow-lg ${
            selected ? 'ring-4 ring-blue-400' : ''
          }`}
          style={{
            background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
            border: '3px solid #fbbf24'
          }}
        />
        <div className="relative z-10 text-center text-xs font-semibold text-gray-800 px-2 max-w-[80px]">
          {data.title}
        </div>
      </div>
      
      {/* Connection handles - HIDDEN but functional */}
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ 
          opacity: 0,
          width: 12,
          height: 12,
          bottom: -6
        }} 
      />
      
      <Handle 
        type="source" 
        position={Position.Left}
        id="yes"
        style={{ 
          opacity: 0,
          width: 12,
          height: 12,
          left: 40
        }} 
      />
      
      <Handle 
        type="source" 
        position={Position.Right}
        id="no"
        style={{ 
          opacity: 0,
          width: 12,
          height: 12,
          right: 40
        }} 
      />
    </>
  );
};

// REVERTED: Use ORIGINAL node types - they were working fine
const nodeTypes = {
  default: ProcessNode,
  process: ProcessNode,
  decision: DecisionNode,
};

export const ReactFlowChart = ({ processData, onNodeClick, onLayoutChange }) => {
  const [isLayouting, setIsLayouting] = useState(false);
  const [layoutDirection, setLayoutDirection] = useState('DOWN');
  const [expandedNodeId, setExpandedNodeId] = useState(null);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [optimizeResult, setOptimizeResult] = useState(null);
  const baseNodePositionsRef = useRef([]);
  const expandedNodesRef = useRef({}); // Track ALL expanded nodes: { nodeId: expandedHeight }
  const pendingNodesRef = useRef(null); // Store nodes waiting to be saved

  // DEBUG: Log processData on mount
  useEffect(() => {
    console.log('🎯 ReactFlowChart mounted with processData:', {
      hasProcessData: !!processData,
      nodeCount: processData?.nodes?.length || 0,
      edgeCount: processData?.edges?.length || 0,
      processDataKeys: processData ? Object.keys(processData) : []
    });
  }, []);

  // Convert backend data structure to ReactFlow format
  const initialNodes = useMemo(() => {
    console.log('📊 Computing initialNodes, processData.nodes:', processData?.nodes?.length || 0);
    
    if (!processData?.nodes || processData.nodes.length === 0) {
      console.warn('⚠️ No nodes in processData!');
      return [];
    }

    const nodes = processData.nodes.map((node) => {
      // CRITICAL FIX: Check BOTH type field AND isDecisionPoint flag
      // Backend sets isDecisionPoint=true but may keep type='action' or 'operational'
      const nodeType = (node.type === 'decision' || node.isDecisionPoint) ? 'decision' : 'process';

      // CRITICAL FIX: Use saved position from database if it exists
      // This preserves user's manual layout adjustments and auto-organized layouts
      const position = node.position && (node.position.x !== 0 || node.position.y !== 0)
        ? node.position
        : { x: 0, y: 0 }; // Only use {0,0} if no saved position exists

      return {
        id: node.id,
        type: nodeType,
        position: position,
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
    
    console.log('✅ Computed', nodes.length, 'initial nodes (with saved positions)');
    return nodes;
  }, [processData]);

  const initialEdges = useMemo(() => {
    if (!processData?.edges || !processData?.nodes) return [];

    // Get all valid node IDs for validation
    const validNodeIds = new Set(processData.nodes.map(n => n.id));
    
    // Create a map of decision nodes for quick lookup
    const decisionNodesMap = new Map();
    processData.nodes.forEach(node => {
      if (node.isDecisionPoint && node.decisionOptions) {
        decisionNodesMap.set(node.id, node.decisionOptions);
      }
    });

    // Filter out edges that reference non-existent nodes (CRITICAL BUG FIX)
    const validEdges = processData.edges.filter(edge => {
      const hasValidSource = validNodeIds.has(edge.source);
      const hasValidTarget = validNodeIds.has(edge.target);
      
      if (!hasValidSource || !hasValidTarget) {
        console.warn(`⚠️ Skipping invalid edge: ${edge.id}`);
        return false;
      }
      
      return true;
    });
    
    // Map edges and add YES/NO labels for decision nodes
    const enhancedEdges = validEdges.map((edge) => {
      // CRITICAL FIX: Add YES/NO labels for decision edges
      let edgeLabel = edge.label || '';
      
      // Check if this edge comes from a decision node
      if (decisionNodesMap.has(edge.source)) {
        const decisionOptions = decisionNodesMap.get(edge.source);
        
        // Determine if this edge is the YES or NO path
        if (decisionOptions.yes === edge.target) {
          edgeLabel = '✓ YES';
        } else if (decisionOptions.no === edge.target) {
          edgeLabel = '✗ NO';
        }
      }
      
      // Determine edge color based on YES/NO
      const isYesEdge = edgeLabel.includes('YES');
      const isNoEdge = edgeLabel.includes('NO');
      const edgeColor = isYesEdge ? '#10b981' : isNoEdge ? '#ef4444' : '#64748b';
      
      return {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edgeLabel,
        type: 'smoothstep',
        animated: true,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 20,
          height: 20,
          color: edgeColor,
        },
        style: {
          strokeWidth: 2,
          stroke: edgeColor,
          strokeDasharray: '5, 5',
        },
        labelStyle: {
          fill: edgeColor,
          fontWeight: 700,
          fontSize: 14,
        },
        labelBgStyle: {
          fill: '#ffffff',
          fillOpacity: 0.95,
          stroke: edgeColor,
          strokeWidth: 1.5,
        },
        labelBgPadding: [12, 8],
        labelBgBorderRadius: 6,
        labelShowBg: true,
        interactionWidth: 20,
      };
    });
    
    return enhancedEdges;
  }, [processData]);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Smart layout adjustment when node expands/collapses
  const handleNodeExpand = useCallback((nodeId, isExpanded, expandedHeight) => {
    console.log('🔄 Node expand/collapse:', { nodeId, isExpanded, expandedHeight });
    
    setNodes((currentNodes) => {
      // Store base positions if not already stored
      if (baseNodePositionsRef.current.length === 0) {
        baseNodePositionsRef.current = currentNodes.map(n => ({ 
          id: n.id, 
          position: { ...n.position } 
        }));
      }
      
      // Find the expanding/collapsing node
      const expandingNode = currentNodes.find(n => n.id === nodeId);
      if (!expandingNode) return currentNodes;
      
      const expandingNodeY = expandingNode.position.y;
      
      // Update expansion tracking
      if (isExpanded) {
        expandedNodesRef.current[nodeId] = expandedHeight || 200;
      } else {
        delete expandedNodesRef.current[nodeId];
      }
      
      // Calculate total height delta from all expanded nodes
      let totalHeightDelta = 0;
      Object.keys(expandedNodesRef.current).forEach(expNodeId => {
        const expNode = currentNodes.find(n => n.id === expNodeId);
        if (expNode && expNode.position.y < expandingNodeY) {
          // If there's an expanded node above, add its delta
          totalHeightDelta += (expandedNodesRef.current[expNodeId] - 100);
        }
      });
      
      // Adjust positions of nodes below the expanding node
      const updatedNodes = currentNodes.map(node => {
        // Don't move the expanding node itself
        if (node.id === nodeId) {
          return node;
        }
        
        // Get the base position (original position before any expansions)
        const basePos = baseNodePositionsRef.current.find(n => n.id === node.id);
        if (!basePos) {
          return node;
        }
        
        // Only move nodes that are below the expanding node
        if (basePos.position.y > expandingNodeY) {
          // Calculate cumulative offset from all expanded nodes above this node
          let cumulativeOffset = 0;
          Object.keys(expandedNodesRef.current).forEach(expNodeId => {
            const expNode = currentNodes.find(n => n.id === expNodeId);
            if (expNode && expNode.position.y < basePos.position.y) {
              // Add the height delta (expanded height - default height of 100)
              cumulativeOffset += (expandedNodesRef.current[expNodeId] - 100);
            }
          });
          
          return {
            ...node,
            position: {
              ...node.position,
              y: basePos.position.y + cumulativeOffset
            }
          };
        }
        
        return node;
      });
      
      console.log('✅ Positions updated for expansion');
      return updatedNodes;
    });
    
    setExpandedNodeId(isExpanded ? nodeId : null);
  }, [setNodes]);

  // Save Layout: Persist optimized layout to database
  const handleSaveLayout = useCallback(async () => {
    if (!pendingNodesRef.current || !onLayoutChange) {
      console.warn('⚠️ No pending changes to save');
      return;
    }
    
    try {
      setIsSaving(true);
      console.log('💾 Saving layout to database...');
      
      await onLayoutChange(pendingNodesRef.current);
      
      // Clear pending changes
      pendingNodesRef.current = null;
      setHasUnsavedChanges(false);
      
      console.log('✅ Layout saved successfully');
      toast.success('✅ Layout saved successfully!');
      
    } catch (error) {
      console.error('❌ Failed to save layout:', error);
      toast.error('Failed to save layout. Please try again.');
    } finally {
      setIsSaving(false);
    }
  }, [onLayoutChange]);

  // Auto-Organize: AI-powered layout optimization
  const handleAutoOrganize = useCallback(async () => {
    try {
      setIsOptimizing(true);
      setOptimizeResult(null);
      
      console.log('✨ Starting auto-organize...');
      
      // Call backend API
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/flowchart/optimize-layout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          nodes: nodes,
          edges: edges,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Layout optimization failed');
      }
      
      const result = await response.json();
      console.log('✅ Optimization complete:', result);
      console.log('🔍 Checking optimizer output - sample nodes:');
      console.log('  Optimizer node 0:', result.optimized_nodes[0]?.id, result.optimized_nodes[0]?.position);
      console.log('  Optimizer node 1:', result.optimized_nodes[1]?.id, result.optimized_nodes[1]?.position);
      
      // Apply optimized positions with smooth animation
      setNodes((currentNodes) => {
        console.log('📐 Current node 0 before update:', currentNodes[0]?.id, currentNodes[0]?.position);
        
        const updated = currentNodes.map((node) => {
          const optimizedNode = result.optimized_nodes.find(n => n.id === node.id);
          if (optimizedNode) {
            console.log(`🔄 Applying optimization to ${node.id}: ${JSON.stringify(node.position)} → ${JSON.stringify(optimizedNode.position)}`);
            return {
              ...node,
              position: optimizedNode.position,
            };
          }
          return node;
        });
        
        console.log('📐 Updated node 0 after map:', updated[0]?.id, updated[0]?.position);
        return updated;
      });
      
      // Update base positions
      baseNodePositionsRef.current = result.optimized_nodes.map(n => ({
        id: n.id,
        position: n.position
      }));
      
      setOptimizeResult(result);
      
      // Store optimized nodes for later save
      pendingNodesRef.current = result.optimized_nodes;
      setHasUnsavedChanges(true);
      
      // Show user prompt to save
      toast.success('✨ Layout optimized! Click "Save Layout" to keep changes.', {
        duration: 5000
      });
      
      // Clear result message after 5 seconds
      setTimeout(() => setOptimizeResult(null), 5000);
      
    } catch (error) {
      console.error('❌ Auto-organize failed:', error);
      alert('Failed to optimize layout. Please try again.');
    } finally {
      setIsOptimizing(false);
    }
  }, [nodes, edges, setNodes]);

  // Apply layout ONLY if nodes don't have saved positions
  useEffect(() => {
    let timeoutId = null;
    let isCancelled = false;
    
    console.log('🔧 Layout effect triggered', {
      initialNodesCount: initialNodes.length,
      initialEdgesCount: initialEdges.length,
      layoutDirection
    });
    
    const applyLayout = async () => {
      if (initialNodes.length === 0) {
        console.warn('⚠️ No initialNodes, skipping layout');
        setIsLayouting(false);
        return;
      }

      // CRITICAL: Check if nodes already have saved positions
      // Only run layout algorithm if ALL nodes are at {0, 0} (fresh flowchart)
      const hasValidPositions = initialNodes.some(node => 
        node.position.x !== 0 || node.position.y !== 0
      );
      
      if (hasValidPositions) {
        console.log('✅ Using saved positions from database (no layout calculation needed)');
        
        // Inject onExpand callback and use positions as-is
        const nodesWithCallbacks = initialNodes.map(node => ({
          ...node,
          data: {
            ...node.data,
            onExpand: handleNodeExpand,
          },
        }));
        
        setNodes(nodesWithCallbacks);
        setEdges(initialEdges);
        setIsLayouting(false);
        return;
      }
      
      // No saved positions - run layout algorithm for new flowchart
      console.log('🚀 No saved positions found - calculating layout for new flowchart...');
      setIsLayouting(true);
      
      try {
        console.log('⏱️ Calling getLayoutedElements...');
        
        // Create cancellable timeout
        const layoutPromise = getLayoutedElements(
          initialNodes,
          initialEdges,
          layoutDirection
        );
        
        const timeoutPromise = new Promise((_, reject) => {
          timeoutId = setTimeout(() => {
            if (!isCancelled) {
              console.error('⏱️ Layout TIMEOUT after 60 seconds!');
              reject(new Error('Layout timeout'));
            }
          }, 60000);
        });
        
        const { nodes: layoutedNodes, edges: layoutedEdges } = await Promise.race([
          layoutPromise,
          timeoutPromise
        ]);
        
        if (isCancelled) {
          console.log('🚫 Layout calculation cancelled');
          return;
        }
        
        console.log('✅ Layout calculation complete!', {
          nodesCount: layoutedNodes.length,
          edgesCount: layoutedEdges.length
        });
        
        // Store base positions in ref
        baseNodePositionsRef.current = layoutedNodes.map(n => ({ id: n.id, position: n.position }));
        
        // Inject onExpand callback
        const nodesWithCallbacks = layoutedNodes.map(node => ({
          ...node,
          data: {
            ...node.data,
            onExpand: handleNodeExpand,
          },
        }));
        
        console.log('📐 Setting nodes and edges...');
        setNodes(nodesWithCallbacks);
        setEdges(layoutedEdges);
        setExpandedNodeId(null);
        expandedNodesRef.current = {};
      } catch (error) {
        console.error('❌ Layout failed:', error);
        // Fallback: Simple vertical layout
        const fallbackNodes = initialNodes.map((node, index) => ({
          ...node,
          position: { x: 100, y: index * 200 },
          data: {
            ...node.data,
            onExpand: handleNodeExpand,
          },
        }));
        console.log('🔄 Using fallback layout');
        setNodes(fallbackNodes);
        setEdges(initialEdges);
      } finally {
        console.log('🏁 Layout complete');
        setIsLayouting(false);
      }
    };

    applyLayout();
    
    return () => {
      isCancelled = true;
      if (timeoutId) {
        clearTimeout(timeoutId);
        console.log('🧹 Layout timeout cleared on cleanup');
      }
    };
  }, [initialNodes, initialEdges, layoutDirection, handleNodeExpand]);

  const handleNodeClick = useCallback((event, node) => {
    if (onNodeClick) {
      onNodeClick(node.data.originalNode);
    }
  }, [onNodeClick]);

  const swimLanes = useMemo(() => {
    if (!processData?.swimLanes) {
      console.log('ℹ️ No swim lanes data from backend');
      return [];
    }
    console.log(`🏊 Swim lanes detected: ${processData.swimLanes.length}`, processData.swimLanes);
    return processData.swimLanes;
  }, [processData]);

  // Calculate swim lane boundaries for visual rendering - MUST BE BEFORE EARLY RETURN
  const swimLaneBoundaries = useMemo(() => {
    if (!swimLanes || swimLanes.length === 0 || nodes.length === 0) {
      if (swimLanes && swimLanes.length > 0) {
        console.warn('⚠️ Swim lanes exist but no nodes yet to calculate boundaries');
      }
      return [];
    }

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

          {/* Auto-Organize & Save Buttons */}
          <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
            {/* Auto-Organize Button */}
            <button
              onClick={handleAutoOrganize}
              disabled={isOptimizing}
              className={`w-full px-3 py-2 text-xs rounded font-medium transition-all ${
                isOptimizing
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-purple-500 to-blue-500 text-white hover:from-purple-600 hover:to-blue-600 shadow-sm hover:shadow-md'
              }`}
            >
              {isOptimizing ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Organizing...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  ✨ Auto-Organize
                </span>
              )}
            </button>
            
            {/* Save Layout Button */}
            <button
              onClick={handleSaveLayout}
              disabled={isSaving || !hasUnsavedChanges}
              className={`w-full px-3 py-2 text-xs rounded font-medium transition-all ${
                isSaving
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : hasUnsavedChanges
                  ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white hover:from-green-600 hover:to-emerald-600 shadow-sm hover:shadow-md'
                  : 'bg-gray-100 text-gray-400 cursor-not-allowed'
              }`}
            >
              {isSaving ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Saving...
                </span>
              ) : hasUnsavedChanges ? (
                <span className="flex items-center justify-center gap-2">
                  💾 Save Layout
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  ✓ Saved
                </span>
              )}
            </button>
            
            {/* Results & Status */}
            {optimizeResult && (
              <div className="mt-2 text-xs text-center">
                <span className="text-green-600 font-medium">
                  Score: {optimizeResult.original_score} → {optimizeResult.layout_score}
                </span>
              </div>
            )}
            
            {hasUnsavedChanges && (
              <div className="mt-2 px-2 py-1 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800 text-center">
                ⚠️ Unsaved changes
              </div>
            )}
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
};
