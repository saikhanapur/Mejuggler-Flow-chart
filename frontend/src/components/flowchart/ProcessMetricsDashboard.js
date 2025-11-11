import React from 'react';

const ProcessMetricsDashboard = ({ process }) => {
  if (!process) return null;

  const complexity = process.complexityScore || {};
  const health = process.healthScore || {};
  const executionTime = process.executionTime || {};
  const metrics = process.processMetrics || {};
  const gapAnalysis = process.gapAnalysis || {};

  const totalGaps = Object.values(gapAnalysis).reduce((sum, gaps) => sum + (gaps?.length || 0), 0);

  return (
    <div className="bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 border-2 border-indigo-200 rounded-xl p-4 shadow-lg mb-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-bold text-indigo-900 flex items-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Process Intelligence
        </h3>
        <div className="text-xs text-indigo-600 font-medium">
          Powered by AI Analysis
        </div>
      </div>

      <div className="grid grid-cols-5 gap-3">
        {/* Complexity Score */}
        <div className="bg-white/80 rounded-lg p-3 border border-indigo-200 hover:shadow-md transition-shadow">
          <div className="text-xs font-semibold text-indigo-700 uppercase mb-1">Complexity</div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-indigo-900">{complexity.score || 'N/A'}</span>
            <span className="text-sm text-indigo-600">/10</span>
          </div>
          <div className={`text-xs font-medium mt-1 ${
            complexity.color === 'red' ? 'text-red-600' :
            complexity.color === 'orange' ? 'text-orange-600' :
            complexity.color === 'yellow' ? 'text-yellow-600' :
            'text-green-600'
          }`}>
            {complexity.level || 'Unknown'}
          </div>
        </div>

        {/* Health Score */}
        <div className="bg-white/80 rounded-lg p-3 border border-indigo-200 hover:shadow-md transition-shadow">
          <div className="text-xs font-semibold text-indigo-700 uppercase mb-1">Health</div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-indigo-900">{health.score || 'N/A'}</span>
            <span className="text-sm text-indigo-600">/100</span>
          </div>
          <div className={`text-xs font-medium mt-1 flex items-center gap-1 ${
            health.color === 'green' ? 'text-green-600' :
            health.color === 'blue' ? 'text-blue-600' :
            health.color === 'yellow' ? 'text-yellow-600' :
            'text-red-600'
          }`}>
            <span>{health.emoji || '💙'}</span>
            <span>{health.level || 'Good'}</span>
          </div>
        </div>

        {/* Execution Time */}
        <div className="bg-white/80 rounded-lg p-3 border border-indigo-200 hover:shadow-md transition-shadow">
          <div className="text-xs font-semibold text-indigo-700 uppercase mb-1">Est. Time</div>
          <div className="text-lg font-bold text-indigo-900">
            {executionTime.average || 'N/A'}
          </div>
          <div className="text-xs text-indigo-600 mt-1">
            {executionTime.bestCase && `${executionTime.bestCase} - ${executionTime.worstCase}`}
          </div>
        </div>

        {/* Process Metrics */}
        <div className="bg-white/80 rounded-lg p-3 border border-indigo-200 hover:shadow-md transition-shadow">
          <div className="text-xs font-semibold text-indigo-700 uppercase mb-1">Structure</div>
          <div className="space-y-0.5 text-xs text-indigo-800">
            <div className="flex justify-between">
              <span>Steps:</span>
              <span className="font-bold">{metrics.totalNodes || 0}</span>
            </div>
            <div className="flex justify-between">
              <span>Decisions:</span>
              <span className="font-bold">{metrics.decisionPoints || 0}</span>
            </div>
            <div className="flex justify-between">
              <span>Loops:</span>
              <span className="font-bold">{metrics.loops || 0}</span>
            </div>
          </div>
        </div>

        {/* Automation & Gaps */}
        <div className="bg-white/80 rounded-lg p-3 border border-indigo-200 hover:shadow-md transition-shadow">
          <div className="text-xs font-semibold text-indigo-700 uppercase mb-1">Quality</div>
          <div className="space-y-0.5 text-xs text-indigo-800">
            <div className="flex justify-between">
              <span>🤖 Auto:</span>
              <span className="font-bold">{metrics.avgAutomation || 0}%</span>
            </div>
            <div className="flex justify-between">
              <span>🔴 Critical:</span>
              <span className="font-bold">{metrics.criticalSteps || 0}</span>
            </div>
            <div className="flex justify-between">
              <span>⚠️ Gaps:</span>
              <span className="font-bold">{totalGaps || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcessMetricsDashboard;
