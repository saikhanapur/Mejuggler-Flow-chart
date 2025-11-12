import React, { useMemo, useState } from 'react';
import FlowNode from './FlowNode';
import ConnectionLine from './ConnectionLine';
import ProgressBadge from './ProgressBadge';
import Legend from './Legend';
import CoverageBadge from './CoverageBadge';
import ProcessMetricsDashboard from './ProcessMetricsDashboard';
import ReferencesModal from './ReferencesModal';
import { api } from '../../utils/api';

/**
 * FlowchartDisplay - Clean, professional flowchart rendering with zoom/pan
 * Based on reference design with AI-driven positioning
 * 
 * Features:
 * - AI-adjusted node positioning (no forced coordinates)
 * - Status-based color coding
 * - Grid dot background
 * - Smart connection lines (vertical/L-shaped)
 * - Conditional quick reference panels (AI determines if needed)
 * - Zoom and pan controls
 */

const FlowchartDisplay = ({ process, onNodeClick, onUpdateNode, selectedNodeId }) => {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [showReferencesModal, setShowReferencesModal] = useState(false);

  if (!process || !process.nodes || process.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <svg className="mx-auto h-12 w-12 text-slate-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <div className="text-slate-700 font-semibold text-lg mb-2">No Flowchart Data</div>
          <div className="text-slate-500 text-sm">Generate a process to see the flowchart</div>
        </div>
      </div>
    );
  }

  // Use backend-provided coordinates (AI decides positioning)
  const nodes = process.nodes || [];
  const edges = process.edges || [];
  const progressStages = process.progressStages || [];
  const quickReference = process.quickReference || {};
  
  // Calculate canvas height based on actual node positions
  const canvasHeight = useMemo(() => {
    if (nodes.length === 0) return 1200;
    const maxY = Math.max(...nodes.map(n => (n.y || n.position?.y || 0)));
    return Math.max(maxY + 400, 1200);
  }, [nodes]);

  // Get unique statuses for legend
  const uniqueStatuses = useMemo(() => {
    return [...new Set(nodes.map(n => n.status || 'operational'))];
  }, [nodes]);

  // Build node map for quick lookup
  const nodeMap = useMemo(() => {
    const map = {};
    nodes.forEach(node => {
      map[node.id] = node;
    });
    return map;
  }, [nodes]);

  // Zoom controls
  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.2, 2));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.2, 0.5));
  const handleResetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };
  const handleFitToScreen = () => {
    setZoom(0.8);
    setPan({ x: 0, y: 0 });
  };

  // Pan controls
  const handleMouseDown = (e) => {
    if (e.target.closest('.flow-node') || e.target.closest('.progress-badge')) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    setPan({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  return (
    <div className="w-full">
      {/* Show References Button */}
      <div className="mb-4 flex items-center justify-between">
        <CoverageBadge 
          metadata={process?.metadata}
          totalNodes={nodes?.length || 0}
        />
        
        <button
          onClick={() => setShowReferencesModal(true)}
          className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white font-bold py-3 px-6 rounded-lg shadow-lg flex items-center gap-2 transition-all transform hover:scale-105"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Show References
        </button>
      </div>
      
      {/* Legend Bar */}
      <Legend statuses={uniqueStatuses} />

      {/* Zoom Controls - Bottom Right, Elegant Design */}
      <div className="fixed bottom-8 right-8 z-30 bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
        <div className="flex flex-col">
          {/* Zoom Display */}
          <div className="px-4 py-2 bg-slate-50 border-b border-slate-200">
            <div className="text-xs font-semibold text-slate-600 text-center">
              Zoom: {Math.round(zoom * 100)}%
            </div>
          </div>
          
          {/* Control Buttons */}
          <div className="p-2 flex flex-col gap-1">
            <button
              onClick={handleZoomIn}
              className="p-2.5 hover:bg-slate-100 rounded-lg transition-colors group"
              title="Zoom In"
            >
              <svg className="w-5 h-5 text-slate-600 group-hover:text-slate-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
              </svg>
            </button>
            
            <button
              onClick={handleZoomOut}
              className="p-2.5 hover:bg-slate-100 rounded-lg transition-colors group"
              title="Zoom Out"
            >
              <svg className="w-5 h-5 text-slate-600 group-hover:text-slate-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M20 12H4" />
              </svg>
            </button>
            
            <div className="h-px bg-slate-200 my-1"></div>
            
            <button
              onClick={handleFitToScreen}
              className="p-2.5 hover:bg-slate-100 rounded-lg transition-colors group"
              title="Fit to Screen"
            >
              <svg className="w-5 h-5 text-slate-600 group-hover:text-slate-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            
            <button
              onClick={handleResetView}
              className="p-2.5 hover:bg-slate-100 rounded-lg transition-colors group"
              title="Reset View (100%)"
            >
              <svg className="w-5 h-5 text-slate-600 group-hover:text-slate-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Flowchart Canvas with Zoom/Pan */}
      <div 
        className={`bg-white rounded-2xl shadow-xl border border-slate-200 p-12 relative overflow-hidden ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
        style={{ minHeight: `${canvasHeight}px` }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {/* Grid Background */}
        <div 
          className="absolute inset-0 opacity-30 pointer-events-none"
          style={{
            backgroundImage: 'radial-gradient(circle, rgb(226, 232, 240) 1px, transparent 1px)',
            backgroundSize: '30px 30px',
          }}
        />

        {/* Zoomable/Pannable Container */}
        <div
          style={{
            transform: `scale(${zoom}) translate(${pan.x / zoom}px, ${pan.y / zoom}px)`,
            transformOrigin: '0 0',
            transition: isDragging ? 'none' : 'transform 0.2s ease-out',
          }}
        >
          {/* Connection Lines (z-index: 1) */}
          {edges.map((edge) => {
            const fromNode = nodeMap[edge.source];
            const toNode = nodeMap[edge.target];
            
            if (!fromNode || !toNode) return null;
            
            // Determine label for decision branches
            let label = null;
            if (fromNode.isDecisionPoint && fromNode.decisionOptions) {
              // Check if this edge is a YES or NO path
              if (fromNode.decisionOptions.yes === toNode.id) {
                label = 'YES';
              } else if (fromNode.decisionOptions.no === toNode.id) {
                label = 'NO';
              }
            }
            
            return (
              <ConnectionLine
                key={edge.id}
                from={fromNode}
                to={toNode}
                type={edge.type || 'solid'}
                label={label}
              />
            );
          })}

          {/* Nodes (z-index: 10) */}
          {nodes.map((node) => (
            <FlowNode
              key={node.id}
              node={node}
              onClick={() => onNodeClick && onNodeClick(node)}
              onUpdateNode={onUpdateNode}
              isSelected={selectedNodeId === node.id}
              selectedNodeId={selectedNodeId}
              isOnCriticalPath={process.criticalPath?.includes(node.id)}
            />
          ))}

          {/* Progress Stage Badges (z-index: 20) */}
          {progressStages.map((stage, i) => (
            <ProgressBadge
              key={`progress-${i}`}
              stage={stage}
            />
          ))}
        </div>
      </div>

      {/* References Modal */}
      <ReferencesModal 
        isOpen={showReferencesModal}
        onClose={() => setShowReferencesModal(false)}
        quickReference={quickReference}
        gapAnalysis={process.gapAnalysis}
      />
    </div>
  );
};

export default FlowchartDisplay;
