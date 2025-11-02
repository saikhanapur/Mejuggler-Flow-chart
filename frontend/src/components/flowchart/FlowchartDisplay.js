import React, { useState } from 'react';
import FlowNode from './FlowNode';
import ConnectionLine from './ConnectionLine';
import ProgressBadge from './ProgressBadge';
import Legend from './Legend';
import QuickReference from './QuickReference';
import EmergencyContacts from './EmergencyContacts';

/**
 * FlowchartDisplay - Pure visual rendering matching reference design
 * Based on: https://saikhanapur.github.io/Complex-SOP/
 * 
 * Features:
 * - Absolute positioned nodes (NO graph libraries)
 * - Status-based color coding
 * - Grid dot background
 * - Connection lines with arrows
 * - Progress stage badges
 * - Quick Reference panels
 */

const FlowchartDisplay = ({ process, onNodeClick, selectedNodeId }) => {
  if (!process || !process.nodes || process.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-slate-400 text-lg mb-2">No flowchart data available</div>
          <div className="text-slate-500 text-sm">Please generate a process first</div>
        </div>
      </div>
    );
  }

  // Don't force positioning - use backend coordinates
  // Backend now handles parallel/sequential intelligently
  const nodes = process.nodes || [];
  
  // Calculate canvas height based on actual positions
  const maxY = nodes.length > 0 
    ? Math.max(...nodes.map(n => n.y || 0)) + 300 
    : 1000;
  const canvasHeight = Math.max(maxY, 1200);

  // Extract quick reference data
  const quickRef = process.quickReference || {};
  const criticalActions = Array.isArray(quickRef.criticalActions) ? quickRef.criticalActions : [];
  const keyTimings = Array.isArray(quickRef.keyTimings) ? quickRef.keyTimings : [];
  const emergencyContacts = (typeof quickRef.emergencyContacts === 'object' && quickRef.emergencyContacts !== null && !Array.isArray(quickRef.emergencyContacts))
    ? quickRef.emergencyContacts
    : {};

  // Get unique statuses for legend
  const uniqueStatuses = [...new Set(nodes.map(n => n.status))];

  return (
    <div className="w-full">
      {/* Legend Bar */}
      <Legend statuses={uniqueStatuses} />

      {/* Flowchart Canvas */}
      <div 
        className="bg-white rounded-2xl shadow-xl border border-slate-200 p-12 relative overflow-visible"
        style={{ minHeight: `${canvasHeight}px` }}
      >
        {/* Grid Background */}
        <div 
          className="absolute inset-0 opacity-30 pointer-events-none rounded-2xl"
          style={{
            backgroundImage: 'radial-gradient(circle, rgb(226, 232, 240) 1px, transparent 1px)',
            backgroundSize: '30px 30px',
          }}
        />

        {/* Connection Lines - Render below nodes */}
        <div className="absolute inset-0" style={{ zIndex: 1 }}>
          {normalizedNodes.map((node, index) => {
            if (index === normalizedNodes.length - 1) return null;
            const nextNode = normalizedNodes[index + 1];
            
            return (
              <ConnectionLine
                key={`line-${node.id}-${nextNode.id}`}
                from={node}
                to={nextNode}
                fromStatus={node.status}
                toStatus={nextNode.status}
              />
            );
          })}
        </div>

        {/* Nodes - Render above lines */}
        <div className="absolute inset-0" style={{ zIndex: 2 }}>
          {normalizedNodes.map((node) => (
            <FlowNode
              key={node.id}
              node={node}
              onClick={() => onNodeClick(node)}
              isSelected={selectedNodeId === node.id}
            />
          ))}
        </div>

        {/* Progress Stage Badges */}
        {process.progressStages && process.progressStages.length > 0 && (
          <div className="absolute inset-0" style={{ zIndex: 3 }}>
            {process.progressStages.map((stage, idx) => (
              <ProgressBadge
                key={`stage-${idx}`}
                type={stage.type}
                x={630}
                y={stage.y || 0}
                title={stage.title}
                description={stage.description}
              />
            ))}
          </div>
        )}
      </div>

      {/* Quick Reference Panels */}
      <QuickReference
        criticalActions={criticalActions}
        keyTimings={keyTimings}
        recoverySteps={normalizedNodes.filter(n => n.status === 'recovery' || n.status === 'verification')}
      />

      {/* Emergency Contacts */}
      {Object.keys(emergencyContacts).length > 0 && (
        <EmergencyContacts contacts={emergencyContacts} />
      )}
    </div>
  );
};

export default FlowchartDisplay;
