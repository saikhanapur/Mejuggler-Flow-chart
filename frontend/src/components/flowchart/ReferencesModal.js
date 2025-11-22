import React from 'react';
import { X, Phone, FileText, Mail, CheckSquare, Wrench, Clock } from 'lucide-react';

const ReferencesModal = ({ isOpen, onClose, quickReference, processName }) => {
  if (!isOpen) return null;

  // Parse the SIMPLIFIED data structure (quick references only)
  const emergencyContacts = quickReference?.emergencyContacts || {};
  const keyScripts = quickReference?.keyScripts || [];
  const criticalTimings = quickReference?.criticalTimings || [];

  // Compact contact display - just name and phone in a list
  const allContacts = Object.entries(emergencyContacts);

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
          {/* Header - Red/Orange gradient */}
          <div className="bg-gradient-to-r from-red-500 to-orange-500 text-white p-6 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-1 flex items-center gap-2">
                <FileText className="w-6 h-6" />
                Quick References
              </h2>
              <p className="text-red-50 text-sm">Contact lists, scripts, and procedures</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-slate-50">
            
            {/* Compact Contact Lists in 2 columns */}
            {allContacts.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Split contacts by location if metadata exists */}
                {(() => {
                  const onshore = allContacts.filter(([_, data]) => {
                    const loc = typeof data === 'object' ? data.location : '';
                    return loc?.toLowerCase().includes('onshore');
                  });
                  const offshore = allContacts.filter(([_, data]) => {
                    const loc = typeof data === 'object' ? data.location : '';
                    return loc?.toLowerCase().includes('offshore');
                  });
                  
                  return (
                    <>
                      {onshore.length > 0 && (
                        <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
                          <h3 className="font-bold text-blue-900 mb-2 text-sm">Onshore Escalation Contacts</h3>
                          <ul className="space-y-1">
                            {onshore.map(([name]) => (
                              <li key={name} className="text-xs text-blue-800">• {name}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {offshore.length > 0 && (
                        <div className="bg-purple-50 rounded-lg border border-purple-200 p-4">
                          <h3 className="font-bold text-purple-900 mb-2 text-sm">Offshore Escalation Contacts</h3>
                          <ul className="space-y-1">
                            {offshore.map(([name]) => (
                              <li key={name} className="text-xs text-purple-800">• {name}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </>
                  );
                })()}
              </div>
            )}

            {/* Individual Contact Cards (only for contacts with full details) */}
            {allContacts.filter(([_, data]) => {
              const phone = typeof data === 'object' ? (data.main || data.phone) : data;
              const hasDetails = phone && phone !== 'Contact details on escalation sheet';
              return hasDetails;
            }).map(([name, contact]) => {
              const phoneNumber = typeof contact === 'object' 
                ? contact.main || contact.phone || ''
                : contact;
              const extension = typeof contact === 'object' ? contact.extension : null;
              const timing = typeof contact === 'object' ? contact.timing : null;
              
              return (
                <div key={name} className="bg-yellow-50 rounded-lg border border-yellow-300 p-4">
                  <h3 className="font-bold text-yellow-900 mb-1 text-sm">{name}</h3>
                  <p className="text-xs font-semibold text-yellow-800">
                    Phone: {phoneNumber}
                    {extension && <span className="ml-2">ext. {extension}</span>}
                  </p>
                  {timing && (
                    <p className="text-xs text-yellow-700 italic mt-1">{timing}</p>
                  )}
                </div>
              );
            })}

            {/* Modica Scripts */}
            {modicaScripts.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {modicaScripts.map((script, idx) => (
                  <div key={idx} className="bg-green-50 rounded-lg border border-green-200 p-4">
                    <h3 className="font-bold text-green-900 mb-2 flex items-center gap-2 text-sm">
                      <FileText className="w-4 h-4" />
                      {script.name}
                    </h3>
                    <div className="space-y-2">
                      {script.content?.outageNotification && (
                        <div>
                          <p className="text-xs font-semibold text-green-800 mb-1">Outage Notification:</p>
                          <p className="text-xs text-green-700 leading-relaxed">{script.content.outageNotification}</p>
                        </div>
                      )}
                      {script.content?.restoration && (
                        <div>
                          <p className="text-xs font-semibold text-green-800 mb-1">Restoration:</p>
                          <p className="text-xs text-green-700 leading-relaxed">{script.content.restoration}</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Email Scripts */}
            {emailScripts.length > 0 && (
              <div className="space-y-3">
                {emailScripts.map((script, idx) => (
                  <div key={idx} className="bg-pink-50 rounded-lg border border-pink-200 p-4">
                    <h3 className="font-bold text-pink-900 mb-2 flex items-center gap-2 text-sm">
                      <Mail className="w-4 h-4" />
                      {script.name}
                    </h3>
                    <div className="space-y-2">
                      {script.content?.outage && (
                        <div className="bg-red-50 border-l-4 border-red-500 p-2 rounded">
                          <p className="text-xs font-semibold text-red-800 mb-1">Outage:</p>
                          <p className="text-xs text-red-700 leading-relaxed">{script.content.outage}</p>
                        </div>
                      )}
                      {script.content?.restoration && (
                        <div className="bg-pink-100 border-l-4 border-pink-500 p-2 rounded">
                          <p className="text-xs font-semibold text-pink-800 mb-1">Restoration:</p>
                          <p className="text-xs text-pink-700 leading-relaxed">{script.content.restoration}</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Checklists */}
            {checklists.length > 0 && (
              <div className="space-y-3">
                {checklists.map((checklist, idx) => (
                  <div key={idx} className="bg-gray-100 rounded-lg border border-gray-300 p-4">
                    <h3 className="font-bold text-gray-900 mb-2 flex items-center gap-2 text-sm">
                      <CheckSquare className="w-4 h-4" />
                      {checklist.name}
                    </h3>
                    {checklist.items && Array.isArray(checklist.items) && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-1">
                        {checklist.items.map((item, itemIdx) => {
                          const itemText = typeof item === 'object'
                            ? (item.text || item.label || item.name || item.description || JSON.stringify(item))
                            : String(item);
                          return (
                            <div key={itemIdx} className="flex items-start gap-2">
                              <span className="text-gray-400 text-xs">□</span>
                              <span className="text-xs text-gray-700">{itemText}</span>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Procedures */}
            {procedures.length > 0 && (
              <div className="space-y-3">
                {procedures.map((procedure, idx) => (
                  <div key={idx} className="bg-blue-50 rounded-lg border border-blue-200 p-4">
                    <h3 className="font-bold text-blue-900 mb-2 flex items-center gap-2 text-sm">
                      <Wrench className="w-4 h-4" />
                      {procedure.name}
                    </h3>
                    {procedure.steps && Array.isArray(procedure.steps) && (
                      <div className="space-y-1">
                        {procedure.steps.map((step, stepIdx) => {
                          const stepText = typeof step === 'object'
                            ? (step.text || step.action || step.description || step.name || JSON.stringify(step))
                            : String(step);
                          return (
                            <div key={stepIdx} className="flex items-start gap-2">
                              <span className="text-blue-600 font-semibold text-xs">{stepIdx + 1}.</span>
                              <p className="text-xs text-blue-800">{stepText}</p>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Key Timings */}
            {keyTimings.length > 0 && (
              <div className="bg-amber-50 rounded-lg border border-amber-200 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="w-4 h-4 text-amber-600" />
                  <h3 className="font-bold text-amber-900 text-sm">Key Timings</h3>
                </div>
                <div className="space-y-1">
                  {keyTimings.map((timing, idx) => {
                    const timingText = typeof timing === 'object'
                      ? (timing.text || timing.description || timing.timing || JSON.stringify(timing))
                      : String(timing);
                    return (
                      <p key={idx} className="text-xs text-amber-800">
                        • {timingText}
                      </p>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Additional References */}
            {supportingReferences.length > 0 && (
              <div className="bg-slate-100 rounded-lg border border-slate-300 p-4">
                <h3 className="font-bold text-slate-900 mb-2 text-sm">Additional References</h3>
                <div className="space-y-1">
                  {supportingReferences.map((ref, idx) => {
                    const refText = typeof ref === 'string' ? ref : (ref.title || ref.name || JSON.stringify(ref));
                    return (
                      <p key={idx} className="text-xs text-slate-700">• {refText}</p>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Empty state */}
            {allContacts.length === 0 && 
             templates.length === 0 && 
             keyTimings.length === 0 &&
             supportingReferences.length === 0 && (
              <div className="text-center py-12 text-slate-500">
                <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium">No reference data available</p>
                <p className="text-sm mt-2">Process references will appear here when available</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReferencesModal;
