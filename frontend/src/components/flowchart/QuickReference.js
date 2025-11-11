import React from 'react';

const QuickReference = ({ criticalActions, keyTimings, recoverySteps }) => {
  return (
    <div className="grid grid-cols-3 gap-6 mt-6">
      {/* Critical Actions */}
      <div className="bg-gradient-to-br from-red-50 to-red-100 border-2 border-red-300 rounded-xl p-6 shadow-lg">
        <h3 className="font-bold text-red-900 mb-4 flex items-center gap-2 text-lg">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Critical Actions
        </h3>
        <div className="space-y-2 text-sm text-red-800">
          {criticalActions && criticalActions.length > 0 ? (
            criticalActions.map((action, idx) => (
              <div key={idx} className="flex items-start gap-2">
                <span className="text-red-600 font-bold">•</span>
                <span>{action}</span>
              </div>
            ))
          ) : (
            <div className="flex items-start gap-2">
              <span className="text-red-600 font-bold">•</span>
              <span>No critical actions identified</span>
            </div>
          )}
        </div>
      </div>

      {/* Key Timings */}
      <div className="bg-gradient-to-br from-amber-50 to-amber-100 border-2 border-amber-300 rounded-xl p-6 shadow-lg">
        <h3 className="font-bold text-amber-900 mb-4 flex items-center gap-2 text-lg">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Key Timings
        </h3>
        <div className="space-y-2 text-sm text-amber-800">
          {keyTimings && keyTimings.length > 0 ? (
            keyTimings.map((timing, idx) => (
              <div key={idx} className="flex items-start gap-2">
                <span className="text-amber-600 font-bold">•</span>
                <span>{timing}</span>
              </div>
            ))
          ) : (
            <div className="flex items-start gap-2">
              <span className="text-amber-600 font-bold">•</span>
              <span>No specific timings mentioned</span>
            </div>
          )}
        </div>
      </div>

      {/* Recovery Steps */}
      <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-2 border-emerald-300 rounded-xl p-6 shadow-lg">
        <h3 className="font-bold text-emerald-900 mb-4 flex items-center gap-2 text-lg">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Recovery Steps
        </h3>
        <div className="space-y-2.5 text-sm text-emerald-800">
          {recoverySteps && recoverySteps.length > 0 ? (
            recoverySteps.map((step, idx) => (
              <div key={idx} className="flex items-start gap-3 p-2 bg-white/40 rounded-lg hover:bg-white/60 transition-colors">
                <div className="flex-shrink-0 w-6 h-6 bg-emerald-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  {idx + 1}
                </div>
                <span className="flex-1 leading-relaxed">{step.title || step}</span>
              </div>
            ))
          ) : (
            <div className="flex items-start gap-3 p-2 bg-white/40 rounded-lg">
              <div className="flex-shrink-0 w-6 h-6 bg-emerald-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                ✓
              </div>
              <span className="flex-1 leading-relaxed">Complete process and document outcomes</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuickReference;
