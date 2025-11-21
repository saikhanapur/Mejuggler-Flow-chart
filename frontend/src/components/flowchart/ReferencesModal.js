import React from 'react';
import { X, Phone, Clock, AlertCircle, FileText } from 'lucide-react';

const ReferencesModal = ({ isOpen, onClose, quickReference, processName }) => {
  if (!isOpen) return null;

  const emergencyContacts = quickReference?.emergencyContacts || {};
  const criticalActions = quickReference?.criticalActions || [];
  const keyTimings = quickReference?.keyTimings || [];

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div className="relative bg-white rounded-2xl shadow-2xl max-w-7xl w-full max-h-[90vh] overflow-hidden flex flex-col">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-1">Process References</h2>
              <p className="text-blue-100 text-sm">Complete documentation and supporting information</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-8 space-y-8 bg-slate-50">
            
            {/* Critical Actions Section */}
            {criticalActions.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <AlertCircle className="w-6 h-6 text-orange-600" />
                  <h3 className="text-xl font-bold text-slate-900">Critical Actions</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {criticalActions.map((action, idx) => {
                    // Extract timing from action text if present (e.g., "Action (10 min)")
                    const timingMatch = action.match(/\((\d+\s*min)\)/i);
                    const timing = timingMatch ? timingMatch[1] : null;
                    const actionText = timing ? action.replace(/\s*\(\d+\s*min\)/i, '') : action;
                    
                    return (
                      <div key={idx} className="bg-white rounded-xl border-2 border-orange-200 p-5 hover:shadow-lg transition-shadow">
                        <div className="flex items-start gap-3">
                          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
                            <span className="text-lg font-bold text-orange-700">{idx + 1}</span>
                          </div>
                          <div className="flex-1">
                            <p className="text-sm font-semibold text-slate-800 leading-snug">
                              {actionText}
                            </p>
                            {timing && (
                              <div className="mt-2 flex items-center gap-1 text-xs text-orange-600">
                                <Clock className="w-3 h-3" />
                                <span>{timing}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Emergency Contacts Section */}
            {Object.keys(emergencyContacts).length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Phone className="w-6 h-6 text-blue-600" />
                  <h3 className="text-xl font-bold text-slate-900">Emergency Contacts</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(emergencyContacts).map(([name, contact]) => {
                    const phoneNumber = typeof contact === 'object' 
                      ? contact.main || contact.phone || ''
                      : contact;
                    const extension = typeof contact === 'object' ? contact.extension : null;
                    const options = typeof contact === 'object' && Array.isArray(contact.options) 
                      ? contact.options 
                      : [];
                    
                    return (
                      <div key={name} className="bg-white rounded-xl border-2 border-blue-200 p-5 hover:shadow-lg transition-shadow">
                        <div className="flex items-start gap-3">
                          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <Phone className="w-5 h-5 text-blue-600" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <h4 className="font-bold text-slate-900 mb-2 text-sm leading-tight">
                              {name}
                            </h4>
                            <p className="text-lg font-semibold text-blue-700 mb-1">
                              {phoneNumber}
                            </p>
                            {extension && (
                              <p className="text-xs text-slate-600 mb-2">
                                Extension: {extension}
                              </p>
                            )}
                            {options.length > 0 && (
                              <div className="mt-2 space-y-1">
                                {options.map((opt, i) => {
                                  const optText = typeof opt === 'object' 
                                    ? `Press ${opt.number}: ${opt.description}`
                                    : opt;
                                  return (
                                    <p key={i} className="text-xs text-slate-600 flex items-center gap-1">
                                      <span className="w-1 h-1 rounded-full bg-slate-400" />
                                      {optText}
                                    </p>
                                  );
                                })}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Key Timings Section */}
            {keyTimings.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Clock className="w-6 h-6 text-purple-600" />
                  <h3 className="text-xl font-bold text-slate-900">Key Timings</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {keyTimings.map((timing, idx) => (
                    <div key={idx} className="bg-white rounded-lg border border-purple-200 p-4 flex items-center gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                        <Clock className="w-4 h-4 text-purple-600" />
                      </div>
                      <p className="text-sm text-slate-700">{timing}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Empty State */}
            {Object.keys(emergencyContacts).length === 0 && 
             criticalActions.length === 0 && 
             keyTimings.length === 0 && (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-500 text-lg">No reference information available</p>
                <p className="text-slate-400 text-sm mt-2">Process references will appear here once extracted</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReferencesModal;
