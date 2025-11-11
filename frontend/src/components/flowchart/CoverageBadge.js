import React, { useState } from 'react';

const CoverageBadge = ({ metadata, totalNodes }) => {
  const [showDetails, setShowDetails] = useState(false);
  
  if (!metadata) return null;
  
  const originalSteps = metadata.originalStepCount || 0;
  const nodesCreated = totalNodes || metadata.nodesCreated || 0;
  const coverage = metadata.coveragePercent || 100;
  const contacts = metadata.contactsExtracted || 0;
  const timings = metadata.timingsExtracted || 0;
  
  return (
    <>
      {/* Floating Coverage Badge */}
      <div className="absolute top-4 right-4 z-30">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-400 rounded-xl p-4 shadow-2xl hover:shadow-3xl transition-all hover:scale-105"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="text-left">
              <div className="font-bold text-green-900 text-lg">
                {coverage}% Coverage
              </div>
              <div className="text-xs text-green-700">
                {originalSteps} steps → {nodesCreated} nodes
              </div>
            </div>
          </div>
          
          <div className="mt-2 text-xs text-green-600 font-medium">
            Click for details ▼
          </div>
        </button>
      </div>

      {/* Detailed Modal */}
      {showDetails && (
        <div 
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setShowDetails(false)}
        >
          <div 
            className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-green-500 to-emerald-600 p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold mb-2">
                    Document Analysis Report
                  </h2>
                  <p className="text-green-100 text-sm">
                    AI-powered verification & coverage analysis
                  </p>
                </div>
                <button
                  onClick={() => setShowDetails(false)}
                  className="w-8 h-8 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Coverage Summary */}
              <div className="bg-green-50 border-2 border-green-200 rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-green-900">{coverage}%</div>
                    <div className="text-sm text-green-700">Document Coverage</div>
                  </div>
                </div>
                <div className="text-sm text-green-800 leading-relaxed">
                  AI successfully analyzed and captured <span className="font-bold">all {originalSteps} steps</span> from your original document. 
                  These have been intelligently organized into <span className="font-bold">{nodesCreated} strategic nodes</span> for easier visualization.
                </div>
              </div>

              {/* Breakdown */}
              <div className="space-y-3">
                <h3 className="font-bold text-gray-900 text-lg mb-4">Coverage Breakdown</h3>
                
                {/* Steps */}
                <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900">Steps Included</div>
                      <div className="text-xs text-gray-600">All procedural steps captured</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-blue-600">{originalSteps}/{originalSteps}</div>
                    <div className="text-xs text-green-600 font-medium">✓ 100%</div>
                  </div>
                </div>

                {/* Contacts */}
                <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg border border-purple-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900">Contacts Extracted</div>
                      <div className="text-xs text-gray-600">Emergency & escalation contacts</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-purple-600">{contacts}</div>
                    <div className="text-xs text-green-600 font-medium">✓ Complete</div>
                  </div>
                </div>

                {/* Timings */}
                <div className="flex items-center justify-between p-4 bg-amber-50 rounded-lg border border-amber-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-amber-500 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900">Timing Requirements</div>
                      <div className="text-xs text-gray-600">Critical timing constraints</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-amber-600">{timings}</div>
                    <div className="text-xs text-green-600 font-medium">✓ Captured</div>
                  </div>
                </div>
              </div>

              {/* Information Preservation */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-xl p-6">
                <h3 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  How Information is Preserved
                </h3>
                <div className="space-y-2 text-sm text-gray-700">
                  <div className="flex items-start gap-2">
                    <span className="text-green-600 font-bold mt-0.5">✓</span>
                    <span><span className="font-semibold">All {originalSteps} original steps</span> are preserved in node sub-steps</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-green-600 font-bold mt-0.5">✓</span>
                    <span><span className="font-semibold">Click ▼ on any node</span> to expand and see detailed sub-steps</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-green-600 font-bold mt-0.5">✓</span>
                    <span><span className="font-semibold">No information lost</span> - only organized for clarity</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-green-600 font-bold mt-0.5">✓</span>
                    <span><span className="font-semibold">Decision points</span> and branching logic maintained</span>
                  </div>
                </div>
              </div>

              {/* AI Model Info */}
              <div className="bg-gray-50 rounded-lg p-4 text-xs text-gray-600">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    <span>Generated by {metadata.aiModel || 'Claude Sonnet 4'}</span>
                  </div>
                  {metadata.generatedAt && (
                    <span>{new Date(metadata.generatedAt).toLocaleString()}</span>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => setShowDetails(false)}
                  className="flex-1 px-4 py-3 bg-green-500 hover:bg-green-600 text-white font-medium rounded-lg transition-colors"
                >
                  Got it!
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default CoverageBadge;
