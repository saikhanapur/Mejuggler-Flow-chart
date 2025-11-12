import React from 'react';

// Status to color mapping
const STATUS_COLORS = {
  trigger: 'rgb(96, 165, 250)',      // blue-400
  critical: 'rgb(244, 63, 94)',      // rose-500
  action: 'rgb(96, 165, 250)',       // blue-400
  communication: 'rgb(168, 85, 247)', // purple-500
  operational: 'rgb(52, 211, 153)',   // emerald-400
  monitoring: 'rgb(251, 191, 36)',    // amber-400
  verification: 'rgb(20, 184, 166)',  // teal-400
  recovery: 'rgb(34, 197, 94)',       // green-500
  warning: 'rgb(251, 191, 36)',       // amber-400
};

const ConnectionLine = ({ from, to, type = 'solid', label = null }) => {
  // Get coordinates
  const x1 = from.x || from.position?.x || 0;
  const y1 = from.y || from.position?.y || 0;
  const x2 = to.x || to.position?.x || 0;
  const y2 = to.y || to.position?.y || 0;

  // Check if from node is a decision
  const isFromDecision = from.isDecisionPoint || false;
  
  // Check if this is a loop edge (going backwards)
  const isLoop = type === 'loop' || type === 'dashed';

  // Center of 240px wide node (or 200px for diamond)
  const fromX = isFromDecision ? x1 + 100 : x1 + 120;
  const fromY = isFromDecision ? y1 + 190 : y1 + 80; // Bottom of from node
  const toX = x2 + 120;
  const toY = y2; // Top of to node

  // Use target node's status for color, or special color for loops
  const color = isLoop ? 'rgb(168, 85, 247)' : (STATUS_COLORS[to.status] || STATUS_COLORS.operational);
  
  // Use dashed for loops
  const isDashed = isLoop;
  const lineWidth = isLoop ? 3 : 2; // Thicker for loops

  const deltaX = Math.abs(toX - fromX);
  const isVertical = deltaX < 50;

  // Vertical line (nodes aligned)
  if (isVertical) {
    const height = toY - fromY;
    if (height <= 0) return null;

    return (
      <>
        {/* Vertical line - ALWAYS SOLID unless explicit loop */}
        <div
          className="absolute pointer-events-none"
          style={{
            left: `${fromX - 1}px`,
            top: `${fromY}px`,
            width: `${lineWidth}px`,
            height: `${height}px`,
            backgroundColor: isDashed ? 'transparent' : color,
            backgroundImage: isDashed
              ? `repeating-linear-gradient(${color} 0, ${color} 4px, transparent 4px, transparent 8px)`
              : 'none',
          }}
        />
        {/* Arrow */}
        <div
          className="absolute w-0 h-0"
          style={{
            left: `${toX - 4}px`,
            top: `${toY - 8}px`,
            borderLeft: '4px solid transparent',
            borderRight: '4px solid transparent',
            borderTop: `8px solid ${color}`,
          }}
        />
        {/* Label for decision branches */}
        {label && (
          <div
            className="absolute bg-white px-2 py-1 rounded text-xs font-bold shadow-sm border"
            style={{
              left: `${fromX + 10}px`,
              top: `${fromY + height / 2 - 10}px`,
              color: color,
              borderColor: color,
            }}
          >
            {label}
          </div>
        )}
      </>
    );
  }

  // L-shaped line (parallel/decision branches)
  const midY = (fromY + toY) / 2;
  const verticalHeight1 = midY - fromY;
  const horizontalWidth = toX - fromX;
  const verticalHeight2 = toY - midY;

  if (verticalHeight1 < 0 || verticalHeight2 < 0) return null;

  return (
    <>
      {/* Vertical segment 1 - ALWAYS SOLID */}
      <div
        className="absolute pointer-events-none"
        style={{
          left: `${fromX - 1}px`,
          top: `${fromY}px`,
          width: `${lineWidth}px`,
          height: `${verticalHeight1}px`,
          backgroundColor: isDashed ? 'transparent' : color,
          backgroundImage: isDashed
            ? `repeating-linear-gradient(${color} 0, ${color} 4px, transparent 4px, transparent 8px)`
            : 'none',
        }}
      />

      {/* Horizontal segment - ALWAYS SOLID */}
      <div
        className="absolute pointer-events-none"
        style={{
          left: horizontalWidth > 0 ? `${fromX}px` : `${toX}px`,
          top: `${midY - 1}px`,
          width: `${Math.abs(horizontalWidth)}px`,
          height: `${lineWidth}px`,
          backgroundColor: isDashed ? 'transparent' : color,
          backgroundImage: isDashed
            ? `repeating-linear-gradient(to right, ${color} 0, ${color} 4px, transparent 4px, transparent 8px)`
            : 'none',
        }}
      />

      {/* Vertical segment 2 - ALWAYS SOLID */}
      <div
        className="absolute pointer-events-none"
        style={{
          left: `${toX - 1}px`,
          top: `${midY}px`,
          width: `${lineWidth}px`,
          height: `${verticalHeight2}px`,
          backgroundColor: isDashed ? 'transparent' : color,
          backgroundImage: isDashed
            ? `repeating-linear-gradient(${color} 0, ${color} 4px, transparent 4px, transparent 8px)`
            : 'none',
        }}
      />

      {/* Arrow */}
      <div
        className="absolute w-0 h-0"
        style={{
          left: `${toX - 4}px`,
          top: `${toY - 8}px`,
          borderLeft: '4px solid transparent',
          borderRight: '4px solid transparent',
          borderTop: `8px solid ${color}`,
        }}
      />

      {/* Label for decision branches */}
      {label && (
        <div
          className="absolute bg-white px-2 py-1 rounded text-xs font-bold shadow-sm border"
          style={{
            left: horizontalWidth > 0 ? `${fromX + Math.abs(horizontalWidth) / 2 - 15}px` : `${toX + Math.abs(horizontalWidth) / 2 - 15}px`,
            top: `${midY - 20}px`,
            color: color,
            borderColor: color,
          }}
        >
          {label}
        </div>
      )}
    </>
  );
};

export default ConnectionLine;
