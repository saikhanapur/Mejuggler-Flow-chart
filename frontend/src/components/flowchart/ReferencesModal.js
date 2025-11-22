import React from 'react';
import { X, Phone, Clock, MessageSquare } from 'lucide-react';

const ReferencesModal = ({ isOpen, onClose, quickReference, processName }) => {
  if (!isOpen) return null;

  // Parse SIMPLIFIED quick references
  const contacts = quickReference?.emergencyContacts || {};
  const scripts = quickReference?.keyScripts || [];
  const timings = quickReference?.criticalTimings || [];

  const contactList = Object.entries(contacts);

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div className="relative bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
          {/* Header */}
          <div className="bg-gradient-to-r from-red-500 to-orange-500 text-white p-6 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-1">Quick References</h2>
              <p className="text-red-50 text-sm">Critical contact info and key points</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Content - Simplified */}
          <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-slate-50">
            
            {/* Info Banner */}
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
              <p className="text-sm text-blue-800">
                <strong>💡 Note:</strong> Full procedures and detailed steps are in the flowchart nodes (click to expand).
                This shows only critical quick-reference information.
              </p>
            </div>

            {/* Emergency Contacts */}
            {contactList.length > 0 && (
              <div className="bg-white rounded-xl border-2 border-slate-200 p-6 shadow-sm">
                <div className="flex items-center gap-2 mb-4">
                  <Phone className="w-5 h-5 text-red-600" />
                  <h3 className="text-lg font-bold text-slate-900">Emergency Contacts</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {contactList.map(([name, data]) => {
                    const phone = typeof data === 'object' ? data.phone : data;
                    const role = typeof data === 'object' ? data.role : '';
                    return (
                      <div key={name} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
                        <Phone className="w-4 h-4 text-red-500 mt-1 flex-shrink-0" />
                        <div>
                          <p className="font-semibold text-slate-900 text-sm">{name}</p>
                          <p className="text-red-600 font-mono text-sm">{phone}</p>
                          {role && <p className="text-slate-600 text-xs mt-1">{role}</p>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Key Scripts */}
            {scripts.length > 0 && (
              <div className="bg-white rounded-xl border-2 border-green-200 p-6 shadow-sm">
                <div className="flex items-center gap-2 mb-4">
                  <MessageSquare className="w-5 h-5 text-green-600" />
                  <h3 className="text-lg font-bold text-slate-900">Key Communication Scripts</h3>
                </div>
                <div className="space-y-3">
                  {scripts.map((script, idx) => {
                    const name = typeof script === 'object' ? script.name : script;
                    const summary = typeof script === 'object' ? script.summary : '';
                    return (
                      <div key={idx} className="p-4 bg-green-50 rounded-lg border border-green-200">
                        <p className="font-semibold text-green-900 text-sm mb-1">{name}</p>
                        {summary && <p className="text-green-700 text-sm">{summary}</p>}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Critical Timings */}
            {timings.length > 0 && (
              <div className="bg-white rounded-xl border-2 border-amber-200 p-6 shadow-sm">
                <div className="flex items-center gap-2 mb-4">
                  <Clock className="w-5 h-5 text-amber-600" />
                  <h3 className="text-lg font-bold text-slate-900">Critical Timings</h3>
                </div>
                <div className="space-y-2">
                  {timings.map((timing, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-sm text-amber-800">
                      <span className="text-amber-500 font-bold">⏱</span>
                      <p>{timing}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Empty state */}
            {contactList.length === 0 && scripts.length === 0 && timings.length === 0 && (
              <div className="text-center py-12 text-slate-500">
                <p className="text-lg font-medium">No quick reference data available</p>
                <p className="text-sm mt-2">All process details are in the flowchart nodes</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReferencesModal;