import React from 'react';

const LEGEND_ITEMS = {
  trigger: {
    label: 'Trigger / Start',
    icon: (
      <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    color: 'bg-gradient-to-br from-blue-500 to-blue-600',
  },
  critical: {
    label: 'Critical / Emergency',
    icon: (
      <svg className="w-4 h-4 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    color: 'bg-gradient-to-br from-rose-500 to-rose-600',
  },
  action: {
    label: 'Action Required',
    icon: (
      <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    ),
    color: 'bg-white border-2 border-blue-400',
  },
  communication: {
    label: 'Communication',
    icon: (
      <svg className="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    color: 'bg-white border-2 border-purple-400',
  },
  operational: {
    label: 'Operational / Active',
    icon: (
      <svg className="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    color: 'bg-white border-2 border-emerald-400',
  },
  monitoring: {
    label: 'Monitoring / Tracking',
    icon: (
      <svg className="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    color: 'bg-white border-2 border-amber-400',
  },
  warning: {
    label: 'Warning / Alert',
    icon: (
      <svg className="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    color: 'bg-white border-2 border-amber-400',
  },
  verification: {
    label: 'Verification / Check',
    icon: (
      <svg className="w-4 h-4 text-teal-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
      </svg>
    ),
    color: 'bg-white border-2 border-teal-400',
  },
  recovery: {
    label: 'Recovery / Resolution',
    icon: (
      <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
    color: 'bg-white border-2 border-green-400',
  },
};

const Legend = ({ statuses = [] }) => {
  if (!statuses || statuses.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow-md border-2 border-slate-200 p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wide">Legend</h3>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <div className="flex items-center gap-1">
            <div className="w-8 h-0.5 bg-slate-400"></div>
            <span>Solid Line = Standard Flow</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-8 h-0.5 border-t-2 border-dashed border-slate-400"></div>
            <span>Dashed = Loop/Repeat</span>
          </div>
        </div>
      </div>
      
      <div className="flex flex-wrap items-center gap-4 text-sm">
        {statuses.map((status) => {
          const item = LEGEND_ITEMS[status];
          if (!item) return null;

          return (
            <div key={status} className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${item.color} shadow-sm`}>
                {item.icon}
              </div>
              <span className="text-slate-700 font-medium">{item.label}</span>
            </div>
          );
        })}
      </div>
      
      {/* Connection line color explanation */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <p className="text-xs text-slate-600">
          <span className="font-semibold">Connection Line Colors:</span> Lines are colored based on the target node's status for visual clarity.
        </p>
      </div>
    </div>
  );
};

export default Legend;
