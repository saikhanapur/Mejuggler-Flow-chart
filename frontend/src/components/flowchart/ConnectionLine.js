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

const ConnectionLine = ({ from, to, fromStatus, toStatus, dashed = false }) => {
  // Use target node's status color
  const color = STATUS_LINE_COLORS[toStatus] || STATUS_LINE_COLORS.action;
  
  // Calculate positions (center of 240px wide node)
  const fromX = from.x + 120;
  const fromY = from.y + 80; // Approximate bottom of node
  const toX = to.x + 120;
  const toY = to.y;
  
  const deltaX = Math.abs(toX - fromX);
  const height = toY - fromY - 10; // Leave small gap before next node
  
  if (height <= 0) return null;
  
  // If nodes are vertically aligned (same X), draw simple vertical line
  if (deltaX < 50) {
    return (
      <>
        {/* Vertical line */}
        <div
          className="absolute"
          style={{
            left: `${fromX}px`,
            top: `${fromY}px`,
            width: '3px', // Thicker for visibility
            height: `${height}px`,
            backgroundColor: dashed ? 'transparent' : color,
            backgroundImage: dashed 
              ? `repeating-linear-gradient(transparent, transparent 8px, ${color} 8px, ${color} 16px)`
              : 'none',
          }}
        />
        {/* Arrow - Larger */}
        {!dashed && (
          <div
            className="absolute"
            style={{
              left: `${fromX - 6}px`,
              top: `${toY - 12}px`,
              width: 0,
              height: 0,
              borderLeft: '6px solid transparent',
              borderRight: '6px solid transparent',
              borderTop: `12px solid ${color}`,
            }}
          />
        )}
      </>
    );
  }
  
  // For parallel branches or decision points, draw L-shaped connection
  const midY = fromY + 40;
  const horizontalWidth = toX - fromX;
  const verticalHeight = toY - midY;
  
  return (
    <>
      {/* Vertical segment 1 */}
      <div
        className="absolute"
        style={{
          left: `${fromX}px`,
          top: `${fromY}px`,
          width: '3px',
          height: `${midY - fromY}px`,
          backgroundColor: dashed ? 'transparent' : color,
          backgroundImage: dashed 
            ? `repeating-linear-gradient(transparent, transparent 8px, ${color} 8px, ${color} 16px)`
            : 'none',
        }}
      />
      
      {/* Horizontal segment */}
      <div
        className="absolute"
        style={{
          left: horizontalWidth > 0 ? `${fromX}px` : `${toX}px`,
          top: `${midY}px`,
          width: `${Math.abs(horizontalWidth)}px`,
          height: '3px',
          backgroundColor: dashed ? 'transparent' : color,
          backgroundImage: dashed 
            ? `repeating-linear-gradient(to right, transparent, transparent 8px, ${color} 8px, ${color} 16px)`
            : 'none',
        }}
      />
      
      {/* Vertical segment 2 */}
      <div
        className="absolute"
        style={{
          left: `${toX}px`,
          top: `${midY}px`,
          width: '3px',
          height: `${verticalHeight}px`,
          backgroundColor: dashed ? 'transparent' : color,
          backgroundImage: dashed 
            ? `repeating-linear-gradient(transparent, transparent 8px, ${color} 8px, ${color} 16px)`
            : 'none',
        }}
      />
      
      {/* Arrow - Larger */}
      {!dashed && (
        <div
          className="absolute"
          style={{
            left: `${toX - 6}px`,
            top: `${toY - 12}px`,
            width: 0,
            height: 0,
            borderLeft: '6px solid transparent',
            borderRight: '6px solid transparent',
            borderTop: `12px solid ${color}`,
          }}
        />
      )}
    </>
  );
};

export default ConnectionLine;
