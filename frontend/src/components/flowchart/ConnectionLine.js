import React from 'react';

// Status to color mapping
const STATUS_LINE_COLORS = {
  critical: '#ef4444',    // red-500
  action: '#3b82f6',      // blue-500
  communication: '#a855f7', // purple-500
  operational: '#10b981',  // emerald-500
  monitoring: '#f59e0b',   // amber-500
  verification: '#14b8a6', // teal-500
  recovery: '#22c55e',     // green-500
};

const ConnectionLine = ({ from, to, fromStatus, toStatus }) => {
  // Use target node's status color
  const color = STATUS_LINE_COLORS[toStatus] || STATUS_LINE_COLORS.action;
  
  // Calculate positions (center of 240px wide node)
  const fromX = from.x + 120;
  const fromY = from.y + 80; // Approximate bottom of node
  const toX = to.x + 120;
  const toY = to.y;
  
  const height = toY - fromY - 10; // Leave small gap before next node
  
  if (height <= 0) return null;
  
  return (
    <>
      {/* Vertical line */}
      <div
        className="absolute"
        style={{
          left: `${fromX}px`,
          top: `${fromY}px`,
          width: '2px',
          height: `${height}px`,
          backgroundColor: color,
        }}
      />
      {/* Arrow */}
      <div
        className="absolute"
        style={{
          left: `${fromX - 4}px`,
          top: `${toY - 10}px`,
          width: 0,
          height: 0,
          borderLeft: '4px solid transparent',
          borderRight: '4px solid transparent',
          borderTop: `8px solid ${color}`,
        }}
      />
    </>
  );
};

export default ConnectionLine;
