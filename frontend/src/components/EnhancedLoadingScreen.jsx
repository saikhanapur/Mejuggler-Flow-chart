/**
 * Enhanced Loading Screen
 * Shows granular, step-by-step progress during document processing
 */
import React, { useState, useEffect, useMemo } from 'react';
import { Check, Loader2, FileText, Brain, GitBranch, Sparkles, Clock } from 'lucide-react';

const PROCESSING_STEPS = [
  {
    id: 'upload',
    label: 'Document uploaded',
    icon: FileText,
    duration: 0, // Instant
    description: 'Your document is ready for processing'
  },
  {
    id: 'extract',
    label: 'Extracting text',
    icon: FileText,
    duration: 8, // seconds
    description: 'Reading and parsing document content'
  },
  {
    id: 'analyze',
    label: 'Analyzing structure',
    icon: Brain,
    duration: 15,
    description: 'AI is identifying processes, steps, and decision points'
  },
  {
    id: 'generate',
    label: 'Generating flowchart',
    icon: GitBranch,
    duration: 10,
    description: 'Building the visual representation'
  },
  {
    id: 'finalize',
    label: 'Finalizing',
    icon: Sparkles,
    duration: 5,
    description: 'Applying final touches and optimizations'
  }
];

const EnhancedLoadingScreen = ({ processingStep }) => {
  const [stepProgress, setStepProgress] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Derive current step index from processingStep text (using useMemo to avoid effect)
  const currentStepIndex = useMemo(() => {
    const stepText = processingStep?.toLowerCase() || '';
    
    if (stepText.includes('upload') || stepText.includes('reading')) {
      return 1;
    } else if (stepText.includes('extract') || stepText.includes('intelligence')) {
      return 1;
    } else if (stepText.includes('analyz') || stepText.includes('structure')) {
      return 2;
    } else if (stepText.includes('generat') || stepText.includes('flowchart') || stepText.includes('building')) {
      return 3;
    } else if (stepText.includes('final') || stepText.includes('prepar')) {
      return 4;
    }
    return 0;
  }, [processingStep]);

  // Progress animation within current step
  useEffect(() => {
    const currentStep = PROCESSING_STEPS[currentStepIndex];
    if (!currentStep || currentStep.duration === 0) {
      return;
    }

    setStepProgress(0);
    const interval = setInterval(() => {
      setStepProgress(prev => {
        const increment = 100 / (currentStep.duration * 10); // Update every 100ms
        return Math.min(prev + increment, 95); // Cap at 95% until step completes
      });
    }, 100);

    return () => clearInterval(interval);
  }, [currentStepIndex]);

  // Elapsed time counter
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Calculate overall progress
  const overallProgress = Math.min(
    ((currentStepIndex / PROCESSING_STEPS.length) * 100) + 
    ((stepProgress / 100) * (100 / PROCESSING_STEPS.length)),
    99
  );

  // Estimate remaining time
  const totalEstimatedTime = PROCESSING_STEPS.reduce((sum, step) => sum + step.duration, 0);
  const estimatedRemaining = Math.max(0, totalEstimatedTime - elapsedTime);

  const currentStep = PROCESSING_STEPS[currentStepIndex];
  const CurrentIcon = currentStep?.icon || Loader2;

  return (
    <div className="flex items-center justify-center min-h-[80vh] p-6">
      <div className="w-full max-w-xl">
        {/* Main Loading Animation */}
        <div className="text-center mb-10">
          <div className="relative w-28 h-28 mx-auto mb-6">
            {/* Outer ring - overall progress */}
            <svg className="w-28 h-28 transform -rotate-90">
              <circle
                cx="56"
                cy="56"
                r="50"
                stroke="#e2e8f0"
                strokeWidth="8"
                fill="none"
              />
              <circle
                cx="56"
                cy="56"
                r="50"
                stroke="url(#gradient)"
                strokeWidth="8"
                fill="none"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 50}`}
                strokeDashoffset={`${2 * Math.PI * 50 * (1 - overallProgress / 100)}`}
                className="transition-all duration-500"
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>
            </svg>
            {/* Center icon */}
            <div className="absolute inset-0 flex items-center justify-center">
              <CurrentIcon className="w-10 h-10 text-blue-600 animate-pulse" />
            </div>
          </div>

          {/* Current Step Text */}
          <h2 className="text-2xl font-bold text-slate-800 mb-2">
            {currentStep?.label || 'Processing...'}
          </h2>
          <p className="text-slate-500 mb-4">
            {currentStep?.description || 'Please wait while we process your document'}
          </p>

          {/* Time Estimate */}
          <div className="flex items-center justify-center gap-2 text-sm text-slate-400">
            <Clock className="w-4 h-4" />
            <span>
              {estimatedRemaining > 0 
                ? `~${estimatedRemaining} seconds remaining`
                : 'Almost done...'}
            </span>
          </div>
        </div>

        {/* Step Progress List */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div className="space-y-4">
            {PROCESSING_STEPS.map((step, index) => {
              const StepIcon = step.icon;
              const isCompleted = index < currentStepIndex;
              const isCurrent = index === currentStepIndex;

              return (
                <div 
                  key={step.id}
                  className={`flex items-center gap-4 p-3 rounded-xl transition-all duration-300 ${
                    isCurrent 
                      ? 'bg-blue-50 border-2 border-blue-200' 
                      : isCompleted 
                        ? 'bg-green-50 border border-green-100'
                        : 'bg-slate-50 border border-slate-100'
                  }`}
                >
                  {/* Step Icon */}
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                    isCompleted 
                      ? 'bg-green-500' 
                      : isCurrent 
                        ? 'bg-blue-500'
                        : 'bg-slate-300'
                  }`}>
                    {isCompleted ? (
                      <Check className="w-5 h-5 text-white" />
                    ) : isCurrent ? (
                      <Loader2 className="w-5 h-5 text-white animate-spin" />
                    ) : (
                      <StepIcon className="w-5 h-5 text-white" />
                    )}
                  </div>

                  {/* Step Label */}
                  <div className="flex-1">
                    <p className={`font-medium ${
                      isCompleted 
                        ? 'text-green-700' 
                        : isCurrent 
                          ? 'text-blue-700'
                          : 'text-slate-400'
                    }`}>
                      {step.label}
                    </p>
                    {isCurrent && (
                      <div className="mt-2">
                        <div className="h-1.5 bg-blue-100 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-500 rounded-full transition-all duration-200"
                            style={{ width: `${stepProgress}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Status Indicator */}
                  <div className="flex-shrink-0">
                    {isCompleted && (
                      <span className="text-xs font-semibold text-green-600">Done</span>
                    )}
                    {isCurrent && (
                      <span className="text-xs font-semibold text-blue-600">
                        {Math.round(stepProgress)}%
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer Tip */}
        <p className="text-center text-xs text-slate-400 mt-6">
          💡 Tip: Larger documents may take longer to process
        </p>
      </div>
    </div>
  );
};

export default EnhancedLoadingScreen;
