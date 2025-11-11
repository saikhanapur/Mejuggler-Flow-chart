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
    details.specificActions.some(action => {
      // Check if action is different from title/description
      const isDifferentFromTitle = action.toLowerCase() !== node.title.toLowerCase();
      const isDifferentFromDesc = action.toLowerCase() !== node.description?.toLowerCase();
      
      // Check if action is different from substeps
      const isDifferentFromSubsteps = !node.subSteps || 
        !node.subSteps.some(substep => substep.toLowerCase() === action.toLowerCase());
      
      return isDifferentFromTitle && isDifferentFromDesc && isDifferentFromSubsteps;
    });

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
    <div className="bg-white rounded-2xl shadow-xl border border-slate-200 h-full overflow-y-auto">
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

        {/* Specific Actions - Only if different from title/description/substeps */}
        {hasMeaningfulActions && (
          <div>
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-3">
              Specific Actions Required
            </h3>
            <div className="space-y-2">
              {details.specificActions
                .filter(action => {
                  // Filter out duplicates with substeps
                  if (node.subSteps) {
                    return !node.subSteps.some(substep => 
                      substep.toLowerCase().trim() === action.toLowerCase().trim()
                    );
                  }
                  return true;
                })
                .map((action, i) => (
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

        {/* Estimated Duration - NEW! */}
        {details.estimatedDuration && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-bold text-blue-900 uppercase tracking-wide mb-2 flex items-center">
              <Clock className="w-4 h-4 mr-2" />
              Estimated Duration
            </h3>
            <p className="text-sm text-blue-800 font-medium">{details.estimatedDuration}</p>
          </div>
        )}

        {/* Dependencies - NEW! */}
        {details.dependencies && details.dependencies.length > 0 && (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-3">
              Prerequisites & Dependencies
            </h3>
            <ul className="space-y-2">
              {details.dependencies.map((dep, i) => (
                <li key={i} className="text-sm text-slate-700 flex items-start gap-2">
                  <span className="text-slate-500 font-bold mt-0.5">•</span>
                  {dep}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Risk Factors - NEW! */}
        {details.riskFactors && details.riskFactors.length > 0 && (
          <div className="bg-amber-50 border-l-4 border-amber-500 rounded-lg p-4">
            <h3 className="text-sm font-bold text-amber-900 uppercase tracking-wide mb-3 flex items-center">
              <AlertTriangle className="w-4 h-4 mr-2" />
              Risk Factors
            </h3>
            <ul className="space-y-2">
              {details.riskFactors.map((risk, i) => (
                <li key={i} className="text-sm text-amber-800 flex items-start gap-2">
                  <span className="text-amber-600 font-bold mt-0.5">⚠</span>
                  {risk}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Success Criteria - NEW! */}
        {details.successCriteria && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
            <h3 className="text-sm font-bold text-emerald-900 uppercase tracking-wide mb-2 flex items-center">
              <CheckCircle className="w-4 h-4 mr-2" />
              Success Criteria
            </h3>
            <p className="text-sm text-emerald-800 leading-relaxed">{details.successCriteria}</p>
          </div>
        )}

        {/* Training Required - NEW! */}
        {details.trainingRequired && (
          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
            <h3 className="text-sm font-bold text-indigo-900 uppercase tracking-wide mb-2">
              Training Required
            </h3>
            <p className="text-sm text-indigo-800 leading-relaxed">{details.trainingRequired}</p>
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

        {/* AI Recommendations - Innovation 1 */}
        {node.aiRecommendations && (
          <div className="bg-gradient-to-br from-purple-50 to-indigo-50 border-2 border-purple-300 rounded-xl p-5 shadow-md">
            <h3 className="text-base font-bold text-purple-900 mb-4 flex items-center gap-2">
              <span className="text-lg">💡</span>
              AI Process Recommendations
            </h3>
            
            {/* Scores */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              {/* Automation Score */}
              <div className="bg-white/80 rounded-lg p-3 border border-purple-200">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-purple-700 uppercase">Automation</span>
                  <span className="text-2xl">🤖</span>
                </div>
                <div className="text-2xl font-bold text-purple-900">
                  {node.aiRecommendations.automationScore}%
                </div>
                <div className="mt-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${
                      node.aiRecommendations.automationScore >= 80 ? 'bg-green-500' :
                      node.aiRecommendations.automationScore >= 50 ? 'bg-yellow-500' :
                      'bg-gray-400'
                    }`}
                    style={{width: `${node.aiRecommendations.automationScore}%`}}
                  ></div>
                </div>
              </div>
              
              {/* Bottleneck Risk */}
              <div className="bg-white/80 rounded-lg p-3 border border-purple-200">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-purple-700 uppercase">Bottleneck</span>
                  <span className="text-2xl">⚠️</span>
                </div>
                <div className="text-2xl font-bold text-purple-900">
                  {node.aiRecommendations.bottleneckRisk}%
                </div>
                <div className="mt-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${
                      node.aiRecommendations.bottleneckRisk >= 80 ? 'bg-red-500' :
                      node.aiRecommendations.bottleneckRisk >= 60 ? 'bg-orange-500' :
                      'bg-yellow-500'
                    }`}
                    style={{width: `${node.aiRecommendations.bottleneckRisk}%`}}
                  ></div>
                </div>
              </div>
            </div>
            
            {/* Suggestions */}
            {node.aiRecommendations.suggestions && node.aiRecommendations.suggestions.length > 0 && (
              <div>
                <h4 className="text-sm font-bold text-purple-900 mb-2">
                  💡 Improvement Suggestions
                </h4>
                <div className="space-y-2">
                  {node.aiRecommendations.suggestions.map((suggestion, idx) => (
                    <div key={idx} className="bg-white/80 rounded-lg p-3 border border-purple-200 flex items-start gap-2">
                      <span className="flex-shrink-0 w-5 h-5 bg-purple-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                        {idx + 1}
                      </span>
                      <span className="text-sm text-purple-900 leading-relaxed">{suggestion}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Rationale */}
            {node.aiRecommendations.rationale && (
              <div className="mt-3 text-xs text-purple-700 italic bg-white/60 rounded-lg p-2 border border-purple-200">
                <strong>AI Analysis:</strong> {node.aiRecommendations.rationale}
              </div>
            )}
          </div>
        )}

        {/* No details message */}
        {!hasAnyDetails && !node.aiRecommendations && (
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
