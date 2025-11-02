import React from 'react';

const LEGEND_ITEMS = {
  trigger: {
    label: 'Trigger',
    color: 'bg-gradient-to-br from-blue-500 to-blue-600',
    textColor: 'text-blue-600',
  },
  critical: {
    label: 'Critical',
    color: 'bg-gradient-to-br from-rose-500 to-rose-600',
    textColor: 'text-rose-600',
  },
  action: {
    label: 'Action',
    color: 'bg-white border-2 border-blue-400',
    textColor: 'text-blue-500',
  },
  communication: {
    label: 'Communication',
    color: 'bg-white border-2 border-purple-400',
    textColor: 'text-purple-500',
  },
  operational: {
    label: 'Operational',
    color: 'bg-white border-2 border-emerald-400',
    textColor: 'text-emerald-500',
  },
  monitoring: {
    label: 'Monitoring',
    color: 'bg-white border-2 border-amber-400',
    textColor: 'text-amber-500',
  },
  warning: {
    label: 'Warning',
    color: 'bg-white border-2 border-amber-400',
    textColor: 'text-amber-500',
  },
  verification: {
    label: 'Verification',
    color: 'bg-white border-2 border-teal-400',
    textColor: 'text-teal-500',
  },
  recovery: {
    label: 'Recovery',
    color: 'bg-white border-2 border-green-400',
    textColor: 'text-green-500',
  },
};

const Legend = ({ statuses = [] }) => {
  if (!statuses || statuses.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 mb-4">
      <div className="flex items-center justify-between gap-6">
        {/* Node Types */}
        <div className="flex items-center gap-4 flex-wrap">
          {statuses.map((status) => {
            const item = LEGEND_ITEMS[status];
            if (!item) return null;

            return (
              <div key={status} className="flex items-center gap-2">
                <div className={`w-6 h-6 rounded-lg ${item.color} shadow-sm`}></div>
                <span className="text-xs font-medium text-slate-700">{item.label}</span>
              </div>
            );
          })}
        </div>
        
        {/* Line Types */}
        <div className="flex items-center gap-4 text-xs text-slate-600">
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-slate-400"></div>
            <span>Flow</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 border-t-2 border-dashed border-slate-400"></div>
            <span>Loop</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Legend;
