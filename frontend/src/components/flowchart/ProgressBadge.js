import React from 'react';

const BADGE_STYLES = {
  immediate: {
    bg: 'bg-red-50',
    border: 'border-red-300',
    titleColor: 'text-red-900',
    textColor: 'text-red-800',
    emoji: '⚠️',
  },
  ongoing: {
    bg: 'bg-amber-50',
    border: 'border-amber-300',
    titleColor: 'text-amber-900',
    textColor: 'text-amber-800',
    emoji: '🔄',
  },
  complete: {
    bg: 'bg-green-50',
    border: 'border-green-300',
    titleColor: 'text-green-900',
    textColor: 'text-green-800',
    emoji: '✅',
  },
};

const ProgressBadge = ({ type, x, y, title, description }) => {
  const style = BADGE_STYLES[type] || BADGE_STYLES.immediate;
  
  return (
    <div
      className={`absolute ${style.bg} border-2 ${style.border} rounded-lg p-3 shadow-sm`}
      style={{ left: `${x}px`, top: `${y}px`, width: '200px' }}
    >
      <div className={`text-xs font-bold ${style.titleColor} mb-1`}>
        {style.emoji} {title}
      </div>
      <div className={`text-xs ${style.textColor}`}>
        {description}
      </div>
    </div>
  );
};

export default ProgressBadge;
