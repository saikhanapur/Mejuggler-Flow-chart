import React from 'react';

const BADGE_STYLES = {
  'IMMEDIATE ACTION': {
    bg: 'bg-rose-100',
    text: 'text-rose-800',
    border: 'border-rose-300',
  },
  'ONGOING': {
    bg: 'bg-amber-100',
    text: 'text-amber-800',
    border: 'border-amber-300',
  },
  'RECOVERY COMPLETE': {
    bg: 'bg-emerald-100',
    text: 'text-emerald-800',
    border: 'border-emerald-300',
  },
};

const ProgressBadge = ({ stage }) => {
  if (!stage || !stage.title) return null;

  const style = BADGE_STYLES[stage.title] || BADGE_STYLES['ONGOING'];
  const x = stage.x || 630;
  const y = stage.y || 0;

  return (
    <div
      className={`absolute px-4 py-2 rounded-lg font-semibold text-xs border-2 ${style.bg} ${style.text} ${style.border} shadow-md`}
      style={{
        left: `${x}px`,
        top: `${y}px`,
        zIndex: 20,
      }}
    >
      {stage.title}
      {stage.description && (
        <div className="text-xs font-normal mt-1 opacity-75">
          {stage.description}
        </div>
      )}
    </div>
  );
};

export default ProgressBadge;
