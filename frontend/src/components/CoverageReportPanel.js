import React, { useState } from 'react';
import { 
  CheckCircle, AlertTriangle, TrendingUp, Package, 
  FileText, ChevronDown, ChevronUp, Info, Target
} from 'lucide-react';

/**
 * Coverage Report Panel
 * 
 * Stage 3 UI: Shows transparency report after flowchart generation
 * Displays what was captured, excluded, and why
 */
const CoverageReportPanel = ({ coverageReport, isOpen, onToggle }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!coverageReport) return null;

  const {
    stepsCaptured = 0,
    stepsExpected = 0,
    completeness = 0,
    nodesWithOperationalDetails = 0,
    decisionNodesMapped = 0,
    swimLanes = 0,
    exclusions = []
  } = coverageReport;

  const completenessColor = 
    completeness >= 90 ? 'text-emerald-600' :
    completeness >= 70 ? 'text-amber-600' :
    'text-red-600';

  const completenessLabel =
    completeness >= 90 ? 'Excellent' :
    completeness >= 70 ? 'Good' :
    'Needs Review';

  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        className="fixed bottom-6 right-6 bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-full shadow-lg hover:shadow-xl transition-all flex items-center gap-2 font-medium group"
      >
        <Info className="w-5 h-5 group-hover:scale-110 transition-transform" />
        View Coverage Report
        <span className={`ml-1 px-2 py-0.5 rounded-full text-xs font-bold ${
          completeness >= 90 ? 'bg-emerald-500' : 'bg-amber-500'
        }`}>
          {completeness}%
        </span>
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 bg-white rounded-2xl shadow-2xl border-2 border-slate-200 overflow-hidden z-40">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            <h3 className="font-bold text-lg">Coverage Report</h3>
          </div>
          <button
            onClick={onToggle}
            className="text-white/80 hover:text-white transition-colors"
          >
            <ChevronDown className="w-5 h-5" />
          </button>
        </div>
        <p className="text-indigo-100 text-xs mt-1">
          AI Transparency Report
        </p>
      </div>

      {/* Main Stats */}
      <div className="p-4 border-b border-slate-200 bg-slate-50">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="text-sm text-slate-600 mb-1">Overall Completeness</div>
            <div className={`text-3xl font-bold ${completenessColor}`}>
              {completeness}%
            </div>
            <div className="text-xs text-slate-500 mt-1">{completenessLabel}</div>
          </div>
          <div className="text-right">
            <div className="text-sm text-slate-600 mb-1">Steps Coverage</div>
            <div className="text-2xl font-bold text-slate-900">
              {stepsCaptured}/{stepsExpected}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${
              completeness >= 90 ? 'bg-emerald-500' :
              completeness >= 70 ? 'bg-amber-500' :
              'bg-red-500'
            }`}
            style={{ width: `${completeness}%` }}
          />
        </div>
      </div>

      {/* Details Grid */}
      <div className="p-4 space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
            <div className="flex items-center gap-2 mb-1">
              <Package className="w-4 h-4 text-blue-600" />
              <div className="text-xs text-slate-600">Operational Details</div>
            </div>
            <div className="text-xl font-bold text-slate-900">
              {nodesWithOperationalDetails}
            </div>
            <div className="text-xs text-slate-500">nodes enriched</div>
          </div>

          <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
            <div className="flex items-center gap-2 mb-1">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <div className="text-xs text-slate-600">Decision Points</div>
            </div>
            <div className="text-xl font-bold text-slate-900">
              {decisionNodesMapped}
            </div>
            <div className="text-xs text-slate-500">mapped</div>
          </div>
        </div>

        {swimLanes > 0 && (
          <div className="bg-indigo-50 rounded-lg p-3 border border-indigo-200">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="w-4 h-4 text-indigo-600" />
              <div className="text-xs text-indigo-700 font-medium">Swim Lanes Detected</div>
            </div>
            <div className="text-lg font-bold text-indigo-900">
              {swimLanes} parallel workflows
            </div>
          </div>
        )}

        {/* Exclusions Section */}
        {exclusions.length > 0 && (
          <div className="border-t border-slate-200 pt-3">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="w-full flex items-center justify-between text-sm font-semibold text-slate-700 hover:text-slate-900 transition-colors"
            >
              <span>Excluded Sections ({exclusions.length})</span>
              {isExpanded ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </button>

            {isExpanded && (
              <div className="mt-2 space-y-2">
                {exclusions.map((exclusion, index) => (
                  <div
                    key={index}
                    className="p-3 bg-slate-50 rounded-lg border border-slate-200"
                  >
                    <div className="text-sm font-medium text-slate-900 mb-1">
                      {exclusion.section}
                    </div>
                    <div className="text-xs text-slate-600 leading-relaxed">
                      {exclusion.reasoning}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Info Message */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex gap-2">
            <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-blue-700 leading-relaxed">
              This report shows AI transparency - what was included in your flowchart and what was intentionally excluded as reference or context.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoverageReportPanel;
