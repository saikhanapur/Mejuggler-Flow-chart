import React, { useMemo } from 'react';
import FlowNode from './FlowNode';
import ConnectionLine from './ConnectionLine';
import ProgressBadge from './ProgressBadge';
import Legend from './Legend';
import QuickReference from './QuickReference';
import EmergencyContacts from './EmergencyContacts';

/**
 * FlowchartDisplay - Clean, professional flowchart rendering
 * Based on reference design with AI-driven positioning
 * 
 * Features:
 * - AI-adjusted node positioning (no forced coordinates)
 * - Status-based color coding
 * - Grid dot background
 * - Smart connection lines (vertical/L-shaped)
 * - Conditional quick reference panels (AI determines if needed)
 */

const FlowchartDisplay = ({ process, onNodeClick, selectedNodeId }) => {
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

  // Determine if quick reference should be shown (AI decision)
  const shouldShowQuickReference = useMemo(() => {
    // Show if AI provided quick reference data with content
    const hasCriticalActions = quickReference.criticalActions && quickReference.criticalActions.length > 0;
    const hasKeyTimings = quickReference.keyTimings && quickReference.keyTimings.length > 0;
    const hasEmergencyContacts = quickReference.emergencyContacts && Object.keys(quickReference.emergencyContacts).length > 0;
    
    return hasCriticalActions || hasKeyTimings || hasEmergencyContacts;
  }, [quickReference]);

  return (
    <div className="w-full">
      {/* Legend Bar */}
      <Legend statuses={uniqueStatuses} />

      {/* Flowchart Canvas */}
      <div 
        className="bg-white rounded-2xl shadow-xl border border-slate-200 p-12 relative overflow-x-auto"
        style={{ minHeight: `${canvasHeight}px` }}
      >
        {/* Grid Background */}
        <div 
          className="absolute inset-0 opacity-30 pointer-events-none"
          style={
            {
            backgroundImage: 'radial-gradient(circle, rgb(226, 232, 240) 1px, transparent 1px)',
            backgroundSize: '30px 30px',
          }}
        />

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
            isSelected={selectedNodeId === node.id}
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

      {/* Conditional Quick Reference Panels - Only if AI determined it's needed */}
      {shouldShowQuickReference && (
        <>
          <QuickReference
            criticalActions={quickReference.criticalActions || []}
            keyTimings={quickReference.keyTimings || []}
            recoverySteps={nodes.filter(n => n.status === 'recovery' || n.status === 'verification')}
          />

          {quickReference.emergencyContacts && Object.keys(quickReference.emergencyContacts).length > 0 && (
            <EmergencyContacts contacts={quickReference.emergencyContacts} />
          )}
        </>
      )}
    </div>
  );
};

export default FlowchartDisplay;
