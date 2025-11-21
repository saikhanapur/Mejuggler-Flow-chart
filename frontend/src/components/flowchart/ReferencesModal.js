import React from 'react';

const ReferencesModal = ({ isOpen, onClose, quickReference, gapAnalysis }) => {
  if (!isOpen) return null;

  const emergencyContacts = quickReference?.emergencyContacts || {};
  const supportingReferences = quickReference?.supportingReferences || [];
  const criticalActions = quickReference?.criticalActions || [];
  const keyTimings = quickReference?.keyTimings || [];
  const recoverySteps = quickReference?.recoverySteps || [];
  
  const gaps = gapAnalysis || {};
  const hasContacts = Object.keys(emergencyContacts).length > 0;
  const hasReferences = supportingReferences.length > 0;
  const hasGaps = Object.values(gaps).some(g => g?.length > 0);

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div className="relative bg-white rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col animate-scale-in">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6 flex items-center justify-between flex-shrink-0">
            <div>
              <h2 className="text-2xl font-bold mb-1">Process References</h2>
              <p className="text-indigo-100 text-sm">Complete documentation and supporting information</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            
            {/* Critical Actions */}
            {criticalActions.length > 0 && (
              <div className="bg-gradient-to-br from-red-50 to-pink-50 border-2 border-red-300 rounded-xl p-5">
                <h3 className="font-bold text-red-900 mb-3 flex items-center gap-2 text-lg">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  Critical Actions
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {criticalActions.map((action, idx) => (
                    <div key={idx} className="bg-white/70 rounded-lg p-3 border border-red-200">
                      <div className="flex items-start gap-2">
                        <span className="flex-shrink-0 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                          {idx + 1}
                        </span>
                        <span className="text-sm text-red-900">{action}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Emergency Contacts */}
            {hasContacts && (
              <div className="bg-gradient-to-br from-pink-50 to-rose-50 border-2 border-pink-300 rounded-xl p-5">
                <h3 className="font-bold text-pink-900 mb-3 flex items-center gap-2 text-lg">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  Emergency Contacts
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {Object.entries(emergencyContacts).map(([name, details], idx) => {
                    // Parse hierarchical contact structure
                    let phoneNumber = '';
                    let extension = null;
                    let options = [];
                    
                    if (typeof details === 'object' && details !== null) {
                      // Handle object format
                      if (details.primary) {
                        phoneNumber = String(details.primary);
                        extension = details.extension;
                        options = details.options || [];
                      } else if (details.main) {
                        phoneNumber = String(details.main);
                        extension = details.extension;
                        options = details.options || [];
                      } else {
                        // Fallback: stringify the object
                        phoneNumber = JSON.stringify(details);
                      }
                    } else if (typeof details === 'string') {
                      // Parse string format: "phone (Extension: X) | Option 1: Y"
                      const parts = details.split('|');
                      phoneNumber = parts[0].trim();
                      
                      // Extract extension
                      const extMatch = phoneNumber.match(/\(Extension:\s*([^)]+)\)/i);
                      if (extMatch) {
                        extension = extMatch[1];
                        phoneNumber = phoneNumber.replace(extMatch[0], '').trim();
                      }
                      
                      // Extract options
                      options = parts.slice(1).map(opt => opt.trim());
                    } else {
                      // Fallback for any other type
                      phoneNumber = String(details || 'No contact info');
                    }
                    
                    // Ensure phoneNumber is always a string
                    phoneNumber = String(phoneNumber);
                    
                    return (
                      <div key={idx} className="bg-white/70 rounded-lg p-4 border border-pink-200">
                        <div className="font-bold text-pink-900 mb-2 flex items-center gap-2">
                          <span className="text-lg">📞</span>
                          {name}
                        </div>
                        <div className="text-sm text-pink-800 space-y-1">
                          <div className="font-semibold">{phoneNumber}</div>
                          {extension && (
                            <div className="text-xs text-pink-600">Extension: {extension}</div>
                          )}
                          {options.length > 0 && (
                            <div className="mt-2 space-y-1">
                              {options.map((opt, i) => {
                                // Handle both string and object formats
                                const optionText = typeof opt === 'object' && opt !== null
                                  ? `Press ${opt.number}: ${opt.description}`
                                  : String(opt);
                                return (
                                  <div key={i} className="text-xs text-pink-700 pl-2 border-l-2 border-pink-300">
                                    {optionText}
                                  </div>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Key Timings */}
            {keyTimings.length > 0 && (
              <div className="bg-gradient-to-br from-amber-50 to-yellow-50 border-2 border-amber-300 rounded-xl p-5">
                <h3 className="font-bold text-amber-900 mb-3 flex items-center gap-2 text-lg">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Key Timings & Schedule
                </h3>
                <div className="grid grid-cols-3 gap-3">
                  {keyTimings.map((timing, idx) => (
                    <div key={idx} className="bg-white/70 rounded-lg p-3 border border-amber-200">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">⏰</span>
                        <span className="text-sm text-amber-900">{timing}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recovery Steps */}
            {recoverySteps.length > 0 && (
              <div className="bg-gradient-to-br from-emerald-50 to-green-50 border-2 border-emerald-300 rounded-xl p-5">
                <h3 className="font-bold text-emerald-900 mb-3 flex items-center gap-2 text-lg">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Recovery Steps
                </h3>
                <div className="space-y-2">
                  {recoverySteps.map((step, idx) => (
                    <div key={idx} className="bg-white/70 rounded-lg p-3 border border-emerald-200 flex items-start gap-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-emerald-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                        {idx + 1}
                      </div>
                      <span className="flex-1 text-sm text-emerald-900 leading-relaxed">
                        {step.title || step}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Supporting References */}
            {hasReferences && (
              <div className="bg-gradient-to-br from-indigo-50 to-blue-50 border-2 border-indigo-300 rounded-xl p-5">
                <h3 className="font-bold text-indigo-900 mb-3 flex items-center gap-2 text-lg">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Supporting References & Documentation
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  {supportingReferences.map((section, idx) => (
                    <div key={idx} className="bg-white/70 rounded-lg p-4 border border-indigo-200">
                      <h4 className="font-bold text-indigo-900 mb-2 flex items-center gap-2">
                        <span className="flex-shrink-0 w-6 h-6 bg-indigo-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                          {idx + 1}
                        </span>
                        {section.title || `Section ${idx + 1}`}
                      </h4>
                      <p className="text-sm text-indigo-800 whitespace-pre-wrap leading-relaxed">
                        {section.content || 'No content provided'}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Gap Analysis */}
            {hasGaps && (
              <div className="bg-gradient-to-br from-orange-50 to-red-50 border-2 border-orange-300 rounded-xl p-5">
                <h3 className="font-bold text-orange-900 mb-3 flex items-center gap-2 text-lg">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  Multi-Lens Gap Analysis
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  {/* Operational Gaps */}
                  {gaps.operational?.length > 0 && (
                    <div className="bg-white/70 rounded-lg p-4 border border-orange-200">
                      <h4 className="font-bold text-orange-900 mb-2 flex items-center gap-2">
                        <span className="text-lg">⚙️</span>
                        Operational
                      </h4>
                      <ul className="space-y-1 text-sm text-orange-800">
                        {gaps.operational.map((gap, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-orange-600 mt-1">•</span>
                            <span>{gap}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {/* Risk Gaps */}
                  {gaps.risk?.length > 0 && (
                    <div className="bg-white/70 rounded-lg p-4 border border-red-200">
                      <h4 className="font-bold text-red-900 mb-2 flex items-center gap-2">
                        <span className="text-lg">⚠️</span>
                        Risk
                      </h4>
                      <ul className="space-y-1 text-sm text-red-800">
                        {gaps.risk.map((gap, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-red-600 mt-1">•</span>
                            <span>{gap}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {/* Compliance Gaps */}
                  {gaps.compliance?.length > 0 && (
                    <div className="bg-white/70 rounded-lg p-4 border border-blue-200">
                      <h4 className="font-bold text-blue-900 mb-2 flex items-center gap-2">
                        <span className="text-lg">📋</span>
                        Compliance
                      </h4>
                      <ul className="space-y-1 text-sm text-blue-800">
                        {gaps.compliance.map((gap, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-blue-600 mt-1">•</span>
                            <span>{gap}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {/* Stakeholder Gaps */}
                  {gaps.stakeholder?.length > 0 && (
                    <div className="bg-white/70 rounded-lg p-4 border border-purple-200">
                      <h4 className="font-bold text-purple-900 mb-2 flex items-center gap-2">
                        <span className="text-lg">👥</span>
                        Stakeholder
                      </h4>
                      <ul className="space-y-1 text-sm text-purple-800">
                        {gaps.stakeholder.map((gap, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-purple-600 mt-1">•</span>
                            <span>{gap}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Empty State */}
            {!hasContacts && !hasReferences && criticalActions.length === 0 && keyTimings.length === 0 && recoverySteps.length === 0 && !hasGaps && (
              <div className="text-center py-12">
                <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="text-lg font-semibold text-gray-700 mb-2">No References Available</h3>
                <p className="text-sm text-gray-500">Reference information will appear here once the document is analyzed</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReferencesModal;
