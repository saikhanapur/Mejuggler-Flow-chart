import React from 'react';
import { X, Phone, Mail, Clock, Server, CheckCircle, AlertTriangle } from 'lucide-react';

const OperationalDetailsPanel = ({ node, onClose }) => {
  if (!node) return null;

  const details = node.operationalDetails || {};
  
  // Intelligent filtering: Only show details that add value
  const hasMeaningfulPurpose = details.purpose && 
    details.purpose !== node.title && 
    details.purpose !== node.description &&
    details.purpose.toLowerCase() !== 'none';

  const hasMeaningfulActions = details.specificActions?.length > 0 &&
    details.specificActions.some(action => 
      action.toLowerCase() !== node.title.toLowerCase() &&
      action.toLowerCase() !== node.description?.toLowerCase()
    );

  const hasContactInfo = details.contactInfo && Object.keys(details.contactInfo).length > 0;
  const hasSystems = details.systems?.length > 0;
  const hasTimeline = details.timeline && details.timeline.toLowerCase() !== 'none';
  const hasEmailTemplates = details.emailTemplates?.length > 0;
  
  const hasMeaningfulGap = details.gap && 
    details.gap.toLowerCase() !== 'none' && 
    details.gap.toLowerCase() !== 'no gap';

  const hasCurrentState = details.currentState;
  const hasIdealState = details.idealState && details.idealState !== details.currentState;

  const hasAnyDetails = 
    hasMeaningfulPurpose ||
    hasMeaningfulActions ||
    details.requiredData?.length > 0 ||
    hasContactInfo ||
    hasSystems ||
    hasTimeline ||
    hasEmailTemplates ||
    hasMeaningfulGap ||
    hasCurrentState ||
    hasIdealState;

  return (
    <div className="fixed right-0 top-16 h-[calc(100vh-4rem)] w-96 bg-white shadow-2xl z-50 overflow-y-auto border-l border-gray-200">
      {/* Header */}
      <div className="sticky top-0 bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6 z-10">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="text-xs font-medium uppercase tracking-wide opacity-90 mb-2">
              {node.type === 'decision' ? 'Decision Point' : 'Process Step'}
            </div>
            <h2 className="text-xl font-bold leading-tight mb-2">{node.title}</h2>
            {node.description && (
              <p className="text-sm opacity-90">{node.description}</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="ml-4 p-2 hover:bg-white/20 rounded-lg transition-colors flex-shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Actors */}
        {node.actors && node.actors.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {node.actors.map((actor, i) => (
              <span
                key={i}
                className="px-3 py-1 bg-white/20 rounded-full text-xs font-medium"
              >
                {actor}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* Purpose - Only if provides new insight */}
        {hasMeaningfulPurpose && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-bold text-blue-900 uppercase tracking-wide mb-2">
              Purpose
            </h3>
            <p className="text-sm text-blue-800 leading-relaxed">{details.purpose}</p>
          </div>
        )}

        {/* Sub-steps */}
        {node.subSteps && node.subSteps.length > 0 && (
          <div>
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-3 flex items-center">
              <CheckCircle className="w-4 h-4 mr-2 text-indigo-600" />
              Sub-steps
            </h3>
            <div className="space-y-2">
              {node.subSteps.map((step, i) => (
                <div key={i} className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-xs font-bold mt-0.5">
                    {i + 1}
                  </div>
                  <div className="ml-3 text-sm text-gray-700">{step}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Decision Criteria */}
        {details.decisionCriteria && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="text-sm font-bold text-yellow-900 uppercase tracking-wide mb-2 flex items-center">
              <AlertTriangle className="w-4 h-4 mr-2" />
              Decision Criteria
            </h3>
            {typeof details.decisionCriteria === 'string' ? (
              <p className="text-sm text-yellow-800">{details.decisionCriteria}</p>
            ) : typeof details.decisionCriteria === 'object' ? (
              <div className="space-y-2 text-sm text-yellow-800">
                {Object.entries(details.decisionCriteria).map(([key, value]) => (
                  <div key={key} className="flex items-start gap-2">
                    <span className="font-semibold capitalize">{key}:</span>
                    <span>{String(value)}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-yellow-800">{String(details.decisionCriteria)}</p>
            )}
          </div>
        )}

        {/* Specific Actions - Only if different from title/description */}
        {hasMeaningfulActions && (
          <div>
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-3">
              Specific Actions Required
            </h3>
            <div className="space-y-2">
              {details.specificActions.map((action, i) => (
                <div key={i} className="flex items-start bg-gray-50 rounded-lg p-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded bg-indigo-600 text-white flex items-center justify-center text-xs font-bold mt-0.5">
                    {i + 1}
                  </div>
                  <div className="ml-3 text-sm text-gray-800">{action}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Required Data */}
        {details.requiredData && details.requiredData.length > 0 && (
          <div>
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-3">
              Required Data Fields
            </h3>
            <div className="grid grid-cols-1 gap-2">
              {details.requiredData.map((field, i) => (
                <div key={i} className="bg-blue-50 border border-blue-200 rounded px-3 py-2 text-sm text-blue-900 font-medium">
                  {field}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Contact Information */}
        {details.contactInfo && Object.keys(details.contactInfo).length > 0 && (
          <div>
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-3 flex items-center">
              <Phone className="w-4 h-4 mr-2 text-indigo-600" />
              Contact Information
            </h3>
            <div className="space-y-2">
              {Object.entries(details.contactInfo).map(([name, contact], i) => (
                <div key={i} className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="font-semibold text-green-900 text-sm">{name}</div>
                  <div className="text-green-700 text-sm mt-1 font-mono">{contact}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Systems/Tools */}
        {details.systems && details.systems.length > 0 && (
          <div>
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-3 flex items-center">
              <Server className="w-4 h-4 mr-2 text-indigo-600" />
              Systems & Tools
            </h3>
            <div className="flex flex-wrap gap-2">
              {details.systems.map((system, i) => (
                <span
                  key={i}
                  className="px-3 py-1.5 bg-purple-100 text-purple-700 rounded-lg text-sm font-medium border border-purple-200"
                >
                  {system}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Timeline - Only if meaningful */}
        {hasTimeline && (
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
            <h3 className="text-sm font-bold text-orange-900 uppercase tracking-wide mb-2 flex items-center">
              <Clock className="w-4 h-4 mr-2" />
              Timeline / SLA
            </h3>
            <p className="text-sm text-orange-800 font-medium">{details.timeline}</p>
          </div>
        )}

        {/* Email Templates */}
        {hasEmailTemplates && (
          <div>
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-3 flex items-center">
              <Mail className="w-4 h-4 mr-2 text-indigo-600" />
              Email / Message Templates
            </h3>
            <div className="space-y-3">
              {details.emailTemplates.map((template, i) => (
                <div key={i} className="bg-gray-50 border border-gray-300 rounded-lg p-4">
                  <pre className="text-xs text-gray-800 whitespace-pre-wrap font-mono">
                    {template}
                  </pre>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Current vs Ideal State - Only if different */}
        {(hasCurrentState || hasIdealState) && (
          <div className="space-y-3">
            {hasCurrentState && (
              <div>
                <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-2">
                  Current State
                </h3>
                <p className="text-sm text-gray-700 bg-gray-50 rounded-lg p-3 leading-relaxed">
                  {details.currentState || node.currentState}
                </p>
              </div>
            )}
            {hasIdealState && (
              <div>
                <h3 className="text-sm font-bold text-emerald-700 uppercase tracking-wide mb-2">
                  Ideal State
                </h3>
                <p className="text-sm text-emerald-800 bg-emerald-50 rounded-lg p-3 leading-relaxed">
                  {details.idealState}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Gap - Only if meaningful */}
        {hasMeaningfulGap && (
          <div className="bg-rose-50 border-l-4 border-rose-500 rounded-lg p-4">
            <h3 className="text-sm font-bold text-rose-900 uppercase tracking-wide mb-2">
              Gap Identified
            </h3>
            <p className="text-sm text-rose-800 leading-relaxed">{details.gap}</p>
          </div>
        )}

        {/* No details message */}
        {!hasAnyDetails && (
          <div className="text-center py-8">
            <div className="text-gray-400 text-sm">
              No operational details available for this step.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OperationalDetailsPanel;
