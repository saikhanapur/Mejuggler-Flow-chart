import React, { useState, useEffect } from 'react';
import { Check, Loader } from 'lucide-react';

const DynamicLoadingScreen = ({ processingStep, analyzing }) => {
  const [currentStatus, setCurrentStatus] = useState(0);

  // Simple, fast-changing statuses (no detailed steps - protect IP)
  const statuses = [
    { icon: '📄', text: 'Reading document...', color: 'indigo' },
    { icon: '🔍', text: 'Analyzing structure...', color: 'purple' },
    { icon: '🧠', text: 'Understanding context...', color: 'blue' },
    { icon: '⚡', text: 'Building flowchart...', color: 'cyan' },
    { icon: '✨', text: 'Finalizing...', color: 'green' }
  ];

  useEffect(() => {
    // Quick status rotation (every 10 seconds)
    const interval = setInterval(() => {
      setCurrentStatus(prev => (prev + 1) % statuses.length);
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const getStepStatus = (stepId) => {
    if (completedSteps.includes(stepId)) return 'complete';
    if (activeSteps.includes(stepId)) return 'active';
    return 'pending';
  };

  return (
    <div className="flex items-center justify-center min-h-[80vh] p-6">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-6"></div>
          
          <h2 className="text-3xl font-bold text-slate-800 mb-3">
            {analyzing ? 'Analyzing Your Document' : 'Generating Your Flowchart'}
          </h2>
          
          <p className="text-lg text-slate-600">
            SuperHumanly AI is processing your document with world-class intelligence
          </p>
        </div>

        {/* Progress Steps */}
        <div className="bg-white rounded-2xl shadow-xl border-2 border-slate-200 p-6 mb-6">
          <div className="space-y-3">
            {allSteps.map((step, index) => {
              const status = getStepStatus(step.id);
              
              return (
                <div 
                  key={step.id}
                  className={`flex items-center gap-4 p-3 rounded-lg transition-all duration-300 ${
                    status === 'complete' ? 'bg-green-50 border border-green-200' :
                    status === 'active' ? 'bg-indigo-50 border border-indigo-300 scale-105' :
                    'bg-slate-50 border border-slate-200 opacity-50'
                  }`}
                >
                  {/* Icon */}
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg ${
                    status === 'complete' ? 'bg-green-500 text-white' :
                    status === 'active' ? 'bg-indigo-500 text-white' :
                    'bg-slate-300 text-slate-600'
                  }`}>
                    {status === 'complete' ? (
                      <Check className="w-5 h-5" />
                    ) : status === 'active' ? (
                      <Loader className="w-5 h-5 animate-spin" />
                    ) : (
                      step.icon
                    )}
                  </div>

                  {/* Label */}
                  <div className="flex-1">
                    <p className={`font-semibold ${
                      status === 'complete' ? 'text-green-900' :
                      status === 'active' ? 'text-indigo-900' :
                      'text-slate-600'
                    }`}>
                      {step.label}
                    </p>
                  </div>

                  {/* Status indicator */}
                  {status === 'active' && (
                    <div className="flex-shrink-0">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-6 border border-indigo-200">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 text-2xl">🚀</div>
            <div>
              <p className="font-bold text-indigo-900 mb-1">What's Happening?</p>
              <p className="text-sm text-indigo-700 leading-relaxed">
                Our AI is analyzing your document with multiple lenses - extracting decisions, loops, swim lanes, 
                calculating complexity, assessing health, identifying bottlenecks, and generating actionable recommendations. 
                This typically takes 1-2 minutes for comprehensive analysis.
              </p>
            </div>
          </div>
        </div>

        {/* Progress indicator */}
        <div className="mt-6 text-center">
          <p className="text-sm text-slate-500">
            {completedSteps.length} of {allSteps.length} analysis steps completed
          </p>
        </div>
      </div>
    </div>
  );
};

export default DynamicLoadingScreen;
