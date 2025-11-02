import React from 'react';

const BADGE_STYLES = {
  'IMMEDIATE ACTION': {
    bg: 'bg-gradient-to-r from-rose-500 to-rose-600',
    text: 'text-white',
    border: 'border-rose-400',
    icon: '⚡',
  },
  'ONGOING': {
    bg: 'bg-gradient-to-r from-amber-500 to-amber-600',
    text: 'text-white',
    border: 'border-amber-400',
    icon: '🔄',
  },
  'RECOVERY COMPLETE': {
    bg: 'bg-gradient-to-r from-emerald-500 to-emerald-600',
    text: 'text-white',
    border: 'border-emerald-400',
    icon: '✓',
  },
  'RECOVERY': {
    bg: 'bg-gradient-to-r from-emerald-500 to-emerald-600',
    text: 'text-white',
    border: 'border-emerald-400',
    icon: '✓',
  },
};

const ProgressBadge = ({ stage }) => {
  if (!stage || !stage.title) return null;

  const style = BADGE_STYLES[stage.title] || BADGE_STYLES['ONGOING'];
  const x = stage.x || 630;
  const y = stage.y || 0;

  return (
    <div
      className={`absolute px-6 py-3 rounded-xl font-bold text-sm border-2 ${style.bg} ${style.text} ${style.border} shadow-2xl transition-all duration-300 hover:scale-105`}
      style={{
        left: `${x}px`,
        top: `${y}px`,
        zIndex: 20,
        minWidth: '200px',
      }}
    >
      <div className="flex items-center gap-2">
        <span className="text-2xl">{style.icon}</span>
        <div className="flex-1">
          <div className="font-bold text-base leading-tight">{stage.title}</div>
          {stage.description && (
            <div className="text-xs font-normal mt-1 opacity-90">
              {stage.description}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProgressBadge;
