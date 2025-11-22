import React from 'react';
import { X, Phone, Clock, FileText, Mail, CheckSquare, Wrench } from 'lucide-react';

const ReferencesModal = ({ isOpen, onClose, quickReference, processName }) => {
  if (!isOpen) return null;

  // Parse the data structure - support both old and new formats
  const emergencyContacts = quickReference?.emergencyContacts || {};
  const keyTimings = quickReference?.keyTimings || [];
  const resources = quickReference?.resources || {};
  const supportingReferences = quickReference?.supportingReferences || [];
  
  // Extract different types of templates/scripts
  const templates = resources?.templates || [];
  const modicaScripts = templates.filter(t => 
    t.name?.toLowerCase().includes('modica') || 
    t.type?.toLowerCase().includes('modica')
  );
  const emailScripts = templates.filter(t => 
    (t.name?.toLowerCase().includes('email') || t.type?.toLowerCase().includes('email')) &&
    !t.name?.toLowerCase().includes('modica')
  );
  const checklists = templates.filter(t => 
    t.name?.toLowerCase().includes('checklist') || 
    t.name?.toLowerCase().includes('timeline') ||
    t.type?.toLowerCase().includes('checklist')
  );
  const procedures = templates.filter(t => 
    (t.name?.toLowerCase().includes('procedure') || 
    t.name?.toLowerCase().includes('process') ||
    t.name?.toLowerCase().includes('dispatch')) &&
    !modicaScripts.includes(t) && !emailScripts.includes(t) && !checklists.includes(t)
  );

  // Split contacts into onshore and offshore if they have that metadata
  const onshoreContacts = Object.entries(emergencyContacts).filter(([name, data]) => {
    const location = typeof data === 'object' ? data.location : '';
    return location?.toLowerCase().includes('onshore');
  });
  const offshoreContacts = Object.entries(emergencyContacts).filter(([name, data]) => {
    const location = typeof data === 'object' ? data.location : '';
    return location?.toLowerCase().includes('offshore');
  });
  const otherContacts = Object.entries(emergencyContacts).filter(([name, data]) => {
    const location = typeof data === 'object' ? data.location : '';
    return !location?.toLowerCase().includes('onshore') && !location?.toLowerCase().includes('offshore');
  });

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
          {/* Header - Red/Orange gradient like reference design */}
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
            
            {/* Contact Cards - Two column layout */}
            {(onshoreContacts.length > 0 || offshoreContacts.length > 0) && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Onshore Escalation Contacts */}
                {onshoreContacts.length > 0 && (
                  <div className="bg-blue-50 rounded-xl border-2 border-blue-200 p-6 shadow-sm">
                    <h3 className="text-lg font-bold text-blue-900 mb-3">Onshore Escalation Contacts</h3>
                    <ul className="space-y-2">
                      {onshoreContacts.map(([name, contact]) => {
                        const role = typeof contact === 'object' ? contact.role : '';
                        return (
                          <li key={name} className="text-sm text-blue-800">
                            <span className="font-medium">• {name}</span>
                            {role && <span className="text-blue-600 ml-1">({role})</span>}
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}

                {/* Offshore Escalation Contacts */}
                {offshoreContacts.length > 0 && (
                  <div className="bg-purple-50 rounded-xl border-2 border-purple-200 p-6 shadow-sm">
                    <h3 className="text-lg font-bold text-purple-900 mb-3">Offshore Escalation Contacts</h3>
                    <ul className="space-y-2">
                      {offshoreContacts.map(([name, contact]) => {
                        const role = typeof contact === 'object' ? contact.role : '';
                        return (
                          <li key={name} className="text-sm text-purple-800">
                            <span className="font-medium">• {name}</span>
                            {role && <span className="text-purple-600 ml-1">({role})</span>}
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Other Contacts (like Wilson IT Contact) */}
            {otherContacts.map(([name, contact]) => {
              const phoneNumber = typeof contact === 'object' 
                ? contact.main || contact.phone || ''
                : contact;
              const extension = typeof contact === 'object' ? contact.extension : null;
              const timing = typeof contact === 'object' ? contact.timing : null;
              const options = typeof contact === 'object' && Array.isArray(contact.options) 
                ? contact.options 
                : [];
              
              return (
                <div key={name} className="bg-yellow-50 rounded-xl border-2 border-yellow-300 p-6 shadow-sm">
                  <h3 className="text-lg font-bold text-yellow-900 mb-2">{name}</h3>
                  <div className="space-y-1">
                    <p className="text-sm font-semibold text-yellow-800">
                      Phone: {phoneNumber}
                      {extension && <span className="ml-2">ext. {extension}</span>}
                    </p>
                    {timing && (
                      <p className="text-sm text-yellow-700 italic">{timing}</p>
                    )}
                    {options.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {options.map((opt, idx) => {
                          const optText = typeof opt === 'object' 
                            ? (opt.label || opt.name || opt.description || JSON.stringify(opt))
                            : String(opt);
                          return (
                            <p key={idx} className="text-sm text-yellow-700">• {optText}</p>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Modica Scripts */}
            {modicaScripts.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {modicaScripts.map((script, idx) => (
                  <div key={idx} className="bg-green-50 rounded-xl border-2 border-green-200 p-6 shadow-sm">
                    <h3 className="text-lg font-bold text-green-900 mb-3 flex items-center gap-2">
                      <FileText className="w-5 h-5" />
                      {script.name}
                    </h3>
                    <div className="space-y-3">
                      {script.content && (
                        <div>
                          {script.content.outageNotification && (
                            <div>
                              <p className="text-sm font-semibold text-green-800 mb-1">Outage Notification:</p>
                              <p className="text-sm text-green-700 leading-relaxed">{script.content.outageNotification}</p>
                            </div>
                          )}
                          {script.content.restoration && (
                            <div className="mt-3">
                              <p className="text-sm font-semibold text-green-800 mb-1">Restoration:</p>
                              <p className="text-sm text-green-700 leading-relaxed">{script.content.restoration}</p>
                            </div>
                          )}
                        </div>
                      )}
                      {!script.content && script.description && (
                        <p className="text-sm text-green-700">{script.description}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Email Scripts */}
            {emailScripts.length > 0 && (
              <div className="space-y-4">
                {emailScripts.map((script, idx) => (
                  <div key={idx} className="bg-pink-50 rounded-xl border-2 border-pink-200 p-6 shadow-sm">
                    <h3 className="text-lg font-bold text-pink-900 mb-3 flex items-center gap-2">
                      <Mail className="w-5 h-5" />
                      {script.name}
                    </h3>
                    <div className="space-y-3">
                      {script.content && (
                        <div>
                          {script.content.outage && (
                            <div className="bg-red-100 border-l-4 border-red-500 p-3 rounded">
                              <p className="text-sm font-semibold text-red-800 mb-1">Outage:</p>
                              <p className="text-sm text-red-700 leading-relaxed">{script.content.outage}</p>
                            </div>
                          )}
                          {script.content.restoration && (
                            <div className="mt-3 bg-pink-100 border-l-4 border-pink-500 p-3 rounded">
                              <p className="text-sm font-semibold text-pink-800 mb-1">Restoration:</p>
                              <p className="text-sm text-pink-700 leading-relaxed">{script.content.restoration}</p>
                            </div>
                          )}
                        </div>
                      )}
                      {!script.content && script.description && (
                        <p className="text-sm text-pink-700">{script.description}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Checklists */}
            {checklists.length > 0 && (
              <div className="space-y-4">
                {checklists.map((checklist, idx) => (
                  <div key={idx} className="bg-gray-100 rounded-xl border-2 border-gray-300 p-6 shadow-sm">
                    <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                      <CheckSquare className="w-5 h-5" />
                      {checklist.name}
                    </h3>
                    {checklist.items && Array.isArray(checklist.items) && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2">
                        {checklist.items.map((item, itemIdx) => (
                          <div key={itemIdx} className="flex items-start gap-2">
                            <span className="text-gray-400 mt-0.5">□</span>
                            <span className="text-sm text-gray-700">{item}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    {checklist.description && !checklist.items && (
                      <p className="text-sm text-gray-700">{checklist.description}</p>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Procedures */}
            {procedures.length > 0 && (
              <div className="space-y-4">
                {procedures.map((procedure, idx) => (
                  <div key={idx} className="bg-blue-50 rounded-xl border-2 border-blue-200 p-6 shadow-sm">
                    <h3 className="text-lg font-bold text-blue-900 mb-3 flex items-center gap-2">
                      <Wrench className="w-5 h-5" />
                      {procedure.name}
                    </h3>
                    {procedure.steps && Array.isArray(procedure.steps) && (
                      <div className="space-y-2">
                        {procedure.steps.map((step, stepIdx) => (
                          <div key={stepIdx} className="flex items-start gap-2">
                            <span className="text-blue-600 font-semibold">{stepIdx + 1}.</span>
                            <p className="text-sm text-blue-800">{step}</p>
                          </div>
                        ))}
                      </div>
                    )}
                    {procedure.description && !procedure.steps && (
                      <p className="text-sm text-blue-700 leading-relaxed">{procedure.description}</p>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Key Timings (if any exist and not already covered) */}
            {keyTimings.length > 0 && (
              <div className="bg-amber-50 rounded-xl border-2 border-amber-200 p-6 shadow-sm">
                <div className="flex items-center gap-2 mb-3">
                  <Clock className="w-5 h-5 text-amber-600" />
                  <h3 className="text-lg font-bold text-amber-900">Key Timings</h3>
                </div>
                <div className="space-y-2">
                  {keyTimings.map((timing, idx) => (
                    <p key={idx} className="text-sm text-amber-800">
                      • {timing}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {/* Supporting References (if any remain) */}
            {supportingReferences.length > 0 && (
              <div className="bg-slate-100 rounded-xl border-2 border-slate-300 p-6 shadow-sm">
                <h3 className="text-lg font-bold text-slate-900 mb-3">Additional References</h3>
                <div className="space-y-2">
                  {supportingReferences.map((ref, idx) => (
                    <p key={idx} className="text-sm text-slate-700">
                      • {typeof ref === 'string' ? ref : ref.title || ref.name}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {/* Empty state */}
            {Object.keys(emergencyContacts).length === 0 && 
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