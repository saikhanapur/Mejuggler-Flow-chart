import React, { useState } from 'react';
import { 
  CheckCircle, XCircle, AlertCircle, FileText, 
  Eye, EyeOff, Edit2, Check, X, Sparkles,
  TrendingUp, Package, Info
} from 'lucide-react';

/**
 * Document Analysis Review Panel
 * 
 * Stage 0 UI: Shows AI's document classification with reasoning
 * User can review, approve, or correct classifications before flowchart generation
 */
const DocumentAnalysisReview = ({ analysis, onApprove, onCancel, isLoading }) => {
  const [sections, setSections] = useState(analysis?.sections || []);
  const [editingSection, setEditingSection] = useState(null);
  const [expandedSections, setExpandedSections] = useState(new Set());

  const classificationColors = {
    flowchartable: 'bg-emerald-50 border-emerald-200 text-emerald-700',
    reference: 'bg-blue-50 border-blue-200 text-blue-700',
    contextual: 'bg-amber-50 border-amber-200 text-amber-700',
    excluded: 'bg-slate-50 border-slate-200 text-slate-500'
  };

  const classificationIcons = {
    flowchartable: CheckCircle,
    reference: Package,
    contextual: Info,
    excluded: XCircle
  };

  const classificationLabels = {
    flowchartable: 'Flowchartable',
    reference: 'Reference Material',
    contextual: 'Context Only',
    excluded: 'Excluded'
  };

  const overallAnalysis = analysis?.overallAnalysis || {};

  const toggleExpand = (sectionId) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const startEdit = (section) => {
    setEditingSection({ ...section });
  };

  const saveEdit = () => {
    const updatedSections = sections.map(s => 
      s.sectionId === editingSection.sectionId ? editingSection : s
    );
    setSections(updatedSections);
    setEditingSection(null);
  };

  const cancelEdit = () => {
    setEditingSection(null);
  };

  const handleApprove = () => {
    const approvedSections = sections
      .filter(s => s.classification === 'flowchartable')
      .map(s => s.sectionId);
    
    const corrections = sections
      .filter(s => {
        const original = analysis.sections.find(os => os.sectionId === s.sectionId);
        return original && original.classification !== s.classification;
      })
      .map(s => {
        const original = analysis.sections.find(os => os.sectionId === s.sectionId);
        return {
          sectionId: s.sectionId,
          from: original.classification,
          to: s.classification,
          reasoning: `User correction: Changed from ${original.classification} to ${s.classification}`
        };
      });

    onApprove({ approvedSections, corrections });
  };

  const flowchartableCount = sections.filter(s => s.classification === 'flowchartable').length;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-4 flex-shrink-0">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Sparkles className="w-5 h-5" />
                <h2 className="text-xl font-bold">Document Intelligence Analysis</h2>
              </div>
              <p className="text-indigo-100 text-xs">
                Review how the AI classified your document sections
              </p>
            </div>
            <button
              onClick={onCancel}
              className="text-white/80 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex-shrink-0">
          <div className="grid grid-cols-4 gap-3">
            <div className="bg-white rounded-lg p-3 border border-slate-200">
              <div className="text-xs text-slate-600 mb-1">Complexity</div>
              <div className="text-lg font-bold text-slate-900 capitalize">
                {overallAnalysis.complexity || 'N/A'}
              </div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-emerald-200">
              <div className="text-xs text-slate-600 mb-1">Flowchartable</div>
              <div className="text-lg font-bold text-emerald-600">
                {flowchartableCount}
              </div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-blue-200">
              <div className="text-xs text-slate-600 mb-1">Reference</div>
              <div className="text-lg font-bold text-blue-600">
                {overallAnalysis.referenceSections || 0}
              </div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-indigo-200">
              <div className="text-xs text-slate-600 mb-1">Est. Steps</div>
              <div className="text-lg font-bold text-indigo-600">
                {overallAnalysis.totalEstimatedSteps || 0}
              </div>
            </div>
          </div>

          {/* Document Summary - Compact */}
          <div className="mt-3 p-3 bg-white rounded-lg border border-slate-200">
            <div className="text-xs font-semibold text-slate-700 mb-1">Summary</div>
            <p className="text-xs text-slate-600 leading-relaxed line-clamp-2">
              {analysis?.documentSummary || 'No summary available'}
            </p>
          </div>
        </div>

        {/* Sections List - Scrollable with Visible Scrollbar */}
        <div 
          className="flex-1 overflow-y-auto p-4 scrollbar-visible" 
          style={{ 
            maxHeight: 'calc(85vh - 280px)',
            scrollbarWidth: 'thin',
            scrollbarColor: '#94a3b8 #e2e8f0'
          }}
        >
          <style>{`
            .scrollbar-visible::-webkit-scrollbar {
              width: 12px;
            }
            .scrollbar-visible::-webkit-scrollbar-track {
              background: #e2e8f0;
              border-radius: 6px;
            }
            .scrollbar-visible::-webkit-scrollbar-thumb {
              background: #94a3b8;
              border-radius: 6px;
            }
            .scrollbar-visible::-webkit-scrollbar-thumb:hover {
              background: #64748b;
            }
          `}</style>
          <div className="space-y-3">
            {sections.map((section) => {
              const Icon = classificationIcons[section.classification];
              const isExpanded = expandedSections.has(section.sectionId);
              const isEditing = editingSection?.sectionId === section.sectionId;

              return (
                <div
                  key={section.sectionId}
                  className={`border-2 rounded-xl transition-all ${
                    classificationColors[section.classification]
                  }`}
                >
                  {/* Section Header - Compact */}
                  <div className="p-3">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-start gap-2 flex-1">
                        <Icon className="w-4 h-4 mt-1 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-sm truncate">
                            {section.title}
                          </h3>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-white/50">
                              {classificationLabels[section.classification]}
                            </span>
                            {section.estimatedSteps && (
                              <span className="text-xs text-slate-600">
                                ~{section.estimatedSteps} steps
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-1 ml-2">
                        <button
                          onClick={() => startEdit(section)}
                          className="p-1.5 hover:bg-white/50 rounded-lg transition-colors"
                          title="Edit classification"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => toggleExpand(section.sectionId)}
                          className="p-1.5 hover:bg-white/50 rounded-lg transition-colors"
                        >
                          {isExpanded ? (
                            <EyeOff className="w-3.5 h-3.5" />
                          ) : (
                            <Eye className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Reasoning - Compact */}
                    <div className="mt-2 p-2 bg-white/50 rounded-lg">
                      <div className="text-xs font-semibold text-slate-600 mb-0.5">
                        AI Reasoning:
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed line-clamp-2">
                        {section.reasoning}
                      </p>
                    </div>

                    {/* Confidence */}
                    {section.confidence && (
                      <div className="mt-1.5 p-1.5 bg-white/30 rounded text-xs text-slate-600">
                        <TrendingUp className="w-3 h-3 inline mr-1" />
                        <span className="font-medium">Confidence:</span> {section.confidence}
                      </div>
                    )}

                    {/* Expanded Details */}
                    {isExpanded && section.content_preview && (
                      <div className="mt-2 p-2 bg-white/30 rounded-lg">
                        <div className="text-xs font-semibold text-slate-600 mb-1">
                          Content Preview:
                        </div>
                        <p className="text-xs text-slate-600 leading-relaxed font-mono">
                          {section.content_preview}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Edit Mode */}
                  {isEditing && (
                    <div className="border-t-2 border-current p-3 bg-white/50">
                      <div className="mb-2">
                        <label className="text-xs font-semibold text-slate-700 mb-1.5 block">
                          Change Classification:
                        </label>
                        <div className="grid grid-cols-2 gap-2">
                          {Object.keys(classificationLabels).map((type) => (
                            <button
                              key={type}
                              onClick={() => setEditingSection({
                                ...editingSection,
                                classification: type
                              })}
                              className={`p-2 rounded-lg border-2 text-xs font-medium transition-all ${
                                editingSection.classification === type
                                  ? classificationColors[type] + ' border-current'
                                  : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                              }`}
                            >
                              {classificationLabels[type]}
                            </button>
                          ))}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={saveEdit}
                          className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-xs font-medium"
                        >
                          <Check className="w-3.5 h-3.5" />
                          Save
                        </button>
                        <button
                          onClick={cancelEdit}
                          className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 transition-colors text-xs font-medium"
                        >
                          <X className="w-3.5 h-3.5" />
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer Actions - Compact */}
        <div className="border-t border-slate-200 p-4 bg-slate-50 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="text-xs text-slate-600">
              {flowchartableCount === 0 ? (
                <span className="text-amber-600 font-medium flex items-center gap-1">
                  <AlertCircle className="w-3.5 h-3.5" />
                  No flowchartable sections. Please reclassify at least one.
                </span>
              ) : (
                <span>
                  Ready to generate from <strong>{flowchartableCount}</strong> section(s)
                </span>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={onCancel}
                className="px-4 py-2 border-2 border-slate-300 text-slate-700 rounded-lg hover:bg-slate-100 transition-colors font-medium text-sm"
              >
                Cancel
              </button>
              <button
                onClick={handleApprove}
                disabled={flowchartableCount === 0 || isLoading}
                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 text-sm ${
                  flowchartableCount === 0 || isLoading
                    ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700'
                }`}
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Flowchart
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
              const Icon = classificationIcons[section.classification];
              const isExpanded = expandedSections.has(section.sectionId);
              const isEditing = editingSection?.sectionId === section.sectionId;

              return (
                <div
                  key={section.sectionId}
                  className={`border-2 rounded-xl transition-all ${
                    classificationColors[section.classification]
                  }`}
                >
                  {/* Section Header */}
                  <div className="p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-start gap-3 flex-1">
                        <Icon className="w-5 h-5 mt-1 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-lg truncate">
                            {section.title}
                          </h3>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs font-medium px-2 py-1 rounded-full bg-white/50">
                              {classificationLabels[section.classification]}
                            </span>
                            {section.estimatedSteps && (
                              <span className="text-xs text-slate-600">
                                ~{section.estimatedSteps} steps
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 ml-4">
                        <button
                          onClick={() => startEdit(section)}
                          className="p-2 hover:bg-white/50 rounded-lg transition-colors"
                          title="Edit classification"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => toggleExpand(section.sectionId)}
                          className="p-2 hover:bg-white/50 rounded-lg transition-colors"
                        >
                          {isExpanded ? (
                            <EyeOff className="w-4 h-4" />
                          ) : (
                            <Eye className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Reasoning (Always Visible) */}
                    <div className="mt-3 p-3 bg-white/50 rounded-lg">
                      <div className="text-xs font-semibold text-slate-600 mb-1">
                        AI Reasoning:
                      </div>
                      <p className="text-sm text-slate-700 leading-relaxed">
                        {section.reasoning}
                      </p>
                    </div>

                    {/* Confidence (Always Visible) */}
                    {section.confidence && (
                      <div className="mt-2 p-2 bg-white/30 rounded text-xs text-slate-600">
                        <TrendingUp className="w-3 h-3 inline mr-1" />
                        <span className="font-medium">Confidence:</span> {section.confidence}
                      </div>
                    )}

                    {/* Expanded Details */}
                    {isExpanded && section.content_preview && (
                      <div className="mt-3 p-3 bg-white/30 rounded-lg">
                        <div className="text-xs font-semibold text-slate-600 mb-1">
                          Content Preview:
                        </div>
                        <p className="text-xs text-slate-600 leading-relaxed font-mono">
                          {section.content_preview}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Edit Mode */}
                  {isEditing && (
                    <div className="border-t-2 border-current p-4 bg-white/50">
                      <div className="mb-3">
                        <label className="text-sm font-semibold text-slate-700 mb-2 block">
                          Change Classification:
                        </label>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                          {Object.keys(classificationLabels).map((type) => (
                            <button
                              key={type}
                              onClick={() => setEditingSection({
                                ...editingSection,
                                classification: type
                              })}
                              className={`p-3 rounded-lg border-2 text-sm font-medium transition-all ${
                                editingSection.classification === type
                                  ? classificationColors[type] + ' border-current'
                                  : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                              }`}
                            >
                              {classificationLabels[type]}
                            </button>
                          ))}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={saveEdit}
                          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm font-medium"
                        >
                          <Check className="w-4 h-4" />
                          Save
                        </button>
                        <button
                          onClick={cancelEdit}
                          className="flex items-center gap-2 px-4 py-2 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 transition-colors text-sm font-medium"
                        >
                          <X className="w-4 h-4" />
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer Actions - Compact */}
        <div className="border-t border-slate-200 p-4 bg-slate-50 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="text-xs text-slate-600">
              {flowchartableCount === 0 ? (
                <span className="text-amber-600 font-medium flex items-center gap-1">
                  <AlertCircle className="w-3.5 h-3.5" />
                  No flowchartable sections. Please reclassify at least one.
                </span>
              ) : (
                <span>
                  Ready to generate from <strong>{flowchartableCount}</strong> section(s)
                </span>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={onCancel}
                className="px-4 py-2 border-2 border-slate-300 text-slate-700 rounded-lg hover:bg-slate-100 transition-colors font-medium text-sm"
              >
                Cancel
              </button>
              <button
                onClick={handleApprove}
                disabled={flowchartableCount === 0 || isLoading}
                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 text-sm ${
                  flowchartableCount === 0 || isLoading
                    ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700'
                }`}
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Flowchart
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentAnalysisReview;
