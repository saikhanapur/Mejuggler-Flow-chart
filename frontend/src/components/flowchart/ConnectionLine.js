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

  // Smart orthogonal routing with better decision branch handling
  const goingLeft = toX < fromX;
  const goingUp = toY < fromY;
  
  // IMPROVED ROUTING: Add more space from source node before horizontal turn
  const verticalGap = 30; // Add 30px vertical space before turning
  const horizontalGap = 20; // Add 20px horizontal padding
  
  // Calculate route points
  let segments = [];
  
  if (goingLeft && !goingUp) {
    // LEFT & DOWN: Exit down, turn left, go down to target
    const turn1Y = fromY + verticalGap;
    const turn2X = toX;
    
    segments = [
      { type: 'vertical', x: fromX, y: fromY, height: verticalGap },
      { type: 'horizontal', x: turn2X, y: turn1Y, width: fromX - turn2X },
      { type: 'vertical', x: turn2X, y: turn1Y, height: toY - turn1Y }
    ];
  } else if (goingUp) {
    // GOING UP (loops): Exit down, go around
    const turn1Y = fromY + 40;
    const sideX = Math.min(fromX, toX) - 60;
    const turn2Y = toY - 40;
    
    segments = [
      { type: 'vertical', x: fromX, y: fromY, height: 40 },
      { type: 'horizontal', x: sideX, y: turn1Y, width: fromX - sideX },
      { type: 'vertical', x: sideX, y: turn1Y, height: turn2Y - turn1Y },
      { type: 'horizontal', x: sideX, y: turn2Y, width: toX - sideX },
      { type: 'vertical', x: toX, y: turn2Y, height: toY - turn2Y }
    ];
  } else {
    // RIGHT & DOWN or STRAIGHT DOWN: Standard L-routing
    const midY = (fromY + toY) / 2;
    
    segments = [
      { type: 'vertical', x: fromX, y: fromY, height: midY - fromY },
      { type: 'horizontal', x: fromX, y: midY, width: toX - fromX },
      { type: 'vertical', x: toX, y: midY, height: toY - midY }
    ];
  }
  
  // Render all segments
  return (
    <>
      {segments.map((segment, idx) => {
        if (segment.type === 'vertical' && segment.height > 0) {
          return (
            <div
              key={`v-${idx}`}
              className="absolute pointer-events-none"
              style={{
                left: `${segment.x - 1}px`,
                top: `${segment.y}px`,
                width: `${lineWidth}px`,
                height: `${segment.height}px`,
                backgroundColor: isDashed ? 'transparent' : color,
                backgroundImage: isDashed
                  ? `repeating-linear-gradient(${color} 0, ${color} 4px, transparent 4px, transparent 8px)`
                  : 'none',
              }}
            />
          );
        } else if (segment.type === 'horizontal' && segment.width !== 0) {
          return (
            <div
              key={`h-${idx}`}
              className="absolute pointer-events-none"
              style={{
                left: segment.width > 0 ? `${segment.x}px` : `${segment.x + segment.width}px`,
                top: `${segment.y - 1}px`,
                width: `${Math.abs(segment.width)}px`,
                height: `${lineWidth}px`,
                backgroundColor: isDashed ? 'transparent' : color,
                backgroundImage: isDashed
                  ? `repeating-linear-gradient(to right, ${color} 0, ${color} 4px, transparent 4px, transparent 8px)`
                  : 'none',
              }}
            />
          );
        }
        return null;
      })}

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

      {/* Label for decision branches - Position on first horizontal segment */}
      {label && (() => {
        const horizontalSegment = segments.find(s => s.type === 'horizontal' && s.width !== 0);
        if (horizontalSegment) {
          const labelX = horizontalSegment.width > 0 
            ? horizontalSegment.x + Math.abs(horizontalSegment.width) / 2 - 15
            : horizontalSegment.x + horizontalSegment.width / 2 - 15;
          
          return (
            <div
              className="absolute bg-white px-2 py-1 rounded text-xs font-bold shadow-sm border"
              style={{
                left: `${labelX}px`,
                top: `${horizontalSegment.y - 20}px`,
                color: color,
                borderColor: color,
              }}
            >
              {label}
            </div>
          );
        }
        return null;
      })()}
    </>
  );
};

export default ConnectionLine;
