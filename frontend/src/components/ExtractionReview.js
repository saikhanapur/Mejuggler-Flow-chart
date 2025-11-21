import React, { useState } from 'react';
import { CheckCircle, FileText, Users, Clock, AlertTriangle, Layers, ChevronDown, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

const ExtractionReview = ({ extractionData, onConfirm, onCancel, isProcessing }) => {
  const [expandedSections, setExpandedSections] = useState({
    contacts: true,
    timings: false,
    actions: false,
    decisions: false,
    swimLanes: false,
    references: false
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Parse extracted data - PRESERVE EVERYTHING
  const contacts = extractionData.emergencyContacts || {};
  const messageTemplates = extractionData.messageTemplates || {};
  const timings = extractionData.keyTimings || [];
  const actions = extractionData.criticalActions || [];
  const systemLinks = extractionData.systemLinks || [];
  const decisions = extractionData.decisionPoints || [];
  const swimLanes = extractionData.swimLanes || [];
  const references = extractionData.supportingReferences || [];

  const totalItems = Object.keys(contacts).length + Object.keys(messageTemplates).length + 
                     timings.length + actions.length + systemLinks.length +
                     decisions.length + swimLanes.length + references.length;

  const Section = ({ title, icon: Icon, count, items, sectionKey, renderItem }) => {
    const isExpanded = expandedSections[sectionKey];
    
    if (count === 0) return null;

    return (
      <div className="border border-slate-200 rounded-lg overflow-hidden">
        <button
          onClick={() => toggleSection(sectionKey)}
          className="w-full flex items-center justify-between p-4 bg-slate-50 hover:bg-slate-100 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Icon className="w-5 h-5 text-blue-600" />
            <span className="font-semibold text-slate-900">{title}</span>
            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
              {count}
            </span>
          </div>
          {isExpanded ? (
            <ChevronDown className="w-5 h-5 text-slate-400" />
          ) : (
            <ChevronRight className="w-5 h-5 text-slate-400" />
          )}
        </button>
        
        {isExpanded && (
          <div className="p-4 bg-white max-h-64 overflow-y-auto">
            {items.length === 0 && Object.keys(items).length === 0 ? (
              <p className="text-slate-500 text-sm">No items found</p>
            ) : (
              renderItem(items)
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-slate-200">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-900">Document Extracted Successfully!</h2>
              <p className="text-slate-600">AI has analyzed your document and found {totalItems} key items</p>
            </div>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 border-b border-slate-200">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="flex items-center gap-2 mb-1">
                <Users className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-slate-600">Contacts</span>
              </div>
              <p className="text-2xl font-bold text-slate-900">{Object.keys(contacts).length}</p>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="flex items-center gap-2 mb-1">
                <Clock className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium text-slate-600">Timings</span>
              </div>
              <p className="text-2xl font-bold text-slate-900">{timings.length}</p>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="flex items-center gap-2 mb-1">
                <AlertTriangle className="w-4 h-4 text-orange-600" />
                <span className="text-sm font-medium text-slate-600">Actions</span>
              </div>
              <p className="text-2xl font-bold text-slate-900">{actions.length}</p>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="flex items-center gap-2 mb-1">
                <FileText className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium text-slate-600">Scripts/Templates</span>
              </div>
              <p className="text-2xl font-bold text-slate-900">{Object.keys(messageTemplates).length}</p>
            </div>
          </div>
        </div>

        {/* Detailed Extraction */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          <Section
            title="Emergency Contacts"
            icon={Users}
            count={Object.keys(contacts).length}
            items={contacts}
            sectionKey="contacts"
            renderItem={(items) => (
              <div className="space-y-3">
                {Object.entries(items).map(([name, contact]) => (
                  <div key={name} className="flex items-start justify-between p-3 bg-slate-50 rounded-lg">
                    <div>
                      <p className="font-semibold text-slate-900">{name}</p>
                      <p className="text-sm text-slate-600 mt-1">
                        {contact.main}
                        {contact.extension && ` ext. ${contact.extension}`}
                      </p>
                      {contact.options && contact.options.length > 0 && (
                        <div className="mt-2 space-y-1">
                          {contact.options.map((opt, idx) => (
                            <p key={idx} className="text-xs text-slate-500">
                              Press {opt.number}: {opt.description}
                            </p>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          />

          <Section
            title="Key Timings"
            icon={Clock}
            count={timings.length}
            items={timings}
            sectionKey="timings"
            renderItem={(items) => (
              <ul className="space-y-2">
                {items.map((timing, idx) => (
                  <li key={idx} className="flex items-start gap-2 p-2 hover:bg-slate-50 rounded">
                    <span className="text-purple-600 font-bold mt-0.5">•</span>
                    <span className="text-sm text-slate-700">{timing}</span>
                  </li>
                ))}
              </ul>
            )}
          />

          <Section
            title="Critical Actions"
            icon={AlertTriangle}
            count={actions.length}
            items={actions}
            sectionKey="actions"
            renderItem={(items) => (
              <ul className="space-y-2">
                {items.map((action, idx) => (
                  <li key={idx} className="flex items-start gap-2 p-2 hover:bg-slate-50 rounded">
                    <span className="text-orange-600 font-bold mt-0.5">•</span>
                    <span className="text-sm text-slate-700">{action}</span>
                  </li>
                ))}
              </ul>
            )}
          />

          <Section
            title="Decision Points"
            icon={AlertTriangle}
            count={decisions.length}
            items={decisions}
            sectionKey="decisions"
            renderItem={(items) => (
              <ul className="space-y-2">
                {items.map((decision, idx) => (
                  <li key={idx} className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm font-semibold text-slate-900">{decision.question || decision}</p>
                    {decision.branches && (
                      <div className="mt-2 space-y-1">
                        <p className="text-xs text-green-700">✓ YES → {decision.branches.yes}</p>
                        <p className="text-xs text-red-700">✗ NO → {decision.branches.no}</p>
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            )}
          />

          <Section
            title="Swim Lanes / Sections"
            icon={Layers}
            count={swimLanes.length}
            items={swimLanes}
            sectionKey="swimLanes"
            renderItem={(items) => (
              <div className="grid grid-cols-2 gap-2">
                {items.map((lane, idx) => (
                  <div key={idx} className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm font-semibold text-blue-900">{lane}</p>
                  </div>
                ))}
              </div>
            )}
          />

          <Section
            title="Supporting References"
            icon={FileText}
            count={references.length}
            items={references}
            sectionKey="references"
            renderItem={(items) => (
              <ul className="space-y-2">
                {items.map((ref, idx) => (
                  <li key={idx} className="flex items-start gap-2 p-2 hover:bg-slate-50 rounded">
                    <FileText className="w-4 h-4 text-slate-400 mt-0.5" />
                    <span className="text-sm text-slate-700">{ref}</span>
                  </li>
                ))}
              </ul>
            )}
          />
        </div>

        {/* Footer Actions */}
        <div className="p-6 border-t border-slate-200 bg-slate-50">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-600">
              Review the extracted information. Click Generate to create your flowchart.
            </p>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={onCancel}
                disabled={isProcessing}
              >
                Cancel
              </Button>
              <Button
                onClick={onConfirm}
                disabled={isProcessing}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8"
              >
                {isProcessing ? 'Generating...' : 'Generate Flowchart →'}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExtractionReview;
