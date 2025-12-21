/**
 * Multi-Process Progress Display
 * 
 * Enterprise-grade real-time progress tracking for long-running operations.
 * Connects to backend SSE stream and displays detailed progress.
 * 
 * Features:
 * - Real-time progress updates via SSE
 * - Per-process progress tracking
 * - Estimated time remaining
 * - Graceful error handling
 * - Connection recovery
 */

import React, { useState, useEffect, useRef } from 'react';
import { Loader2, CheckCircle, AlertCircle, Clock, Zap, FileText, GitBranch } from 'lucide-react';

const PHASE_ICONS = {
  extracting_section: FileText,
  analyzing_structure: Zap,
  generating_flowchart: GitBranch,
  completed: CheckCircle,
};

const PHASE_LABELS = {
  extracting_section: 'Extracting Section',
  analyzing_structure: 'Analyzing Structure',
  generating_flowchart: 'Building Flowchart',
  completed: 'Completed',
};

const MultiProcessProgress = ({ 
  sessionId, 
  processTitles = [], 
  onComplete,
  onError 
}) => {
  const [progress, setProgress] = useState({
    currentStep: 0,
    totalSteps: processTitles.length || 1,
    currentPhase: 'initializing',
    currentMessage: 'Starting...',
    overallProgress: 0,
    elapsedSeconds: 0,
    estimatedRemainingSeconds: 60,
    stepsCompleted: [],
    isComplete: false,
    isError: false,
  });
  
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const eventSourceRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    if (!sessionId) return;

    const connectSSE = () => {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const url = `${backendUrl}/api/progress/${sessionId}`;
      
      console.log(`📡 Connecting to progress stream: ${url}`);
      setConnectionStatus('connecting');

      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.addEventListener('progress', (event) => {
        try {
          const data = JSON.parse(event.data);
          setProgress(prev => ({
            ...prev,
            ...data,
          }));
          setConnectionStatus('connected');
        } catch (e) {
          console.error('Failed to parse progress event:', e);
        }
      });

      eventSource.addEventListener('complete', (event) => {
        try {
          const data = JSON.parse(event.data);
          setProgress(prev => ({
            ...prev,
            ...data,
            isComplete: true,
          }));
          setConnectionStatus('completed');
          
          if (onComplete) {
            onComplete(data.result);
          }
          
          eventSource.close();
        } catch (e) {
          console.error('Failed to parse complete event:', e);
        }
      });

      eventSource.addEventListener('error', (event) => {
        try {
          const data = JSON.parse(event.data);
          setProgress(prev => ({
            ...prev,
            isError: true,
            errorMessage: data.errorMessage,
          }));
          setConnectionStatus('error');
          
          if (onError) {
            onError(data.errorMessage);
          }
          
          eventSource.close();
        } catch (e) {
          // Connection error, not a data error
          console.error('SSE connection error:', e);
          setConnectionStatus('reconnecting');
          
          // Attempt reconnection after delay
          reconnectTimeoutRef.current = setTimeout(() => {
            connectSSE();
          }, 3000);
        }
      });

      eventSource.addEventListener('keepalive', () => {
        // Just a keepalive, no action needed
        setConnectionStatus('connected');
      });

      eventSource.onerror = () => {
        if (eventSource.readyState === EventSource.CLOSED) {
          setConnectionStatus('disconnected');
        }
      };
    };

    connectSSE();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [sessionId, onComplete, onError]);

  const formatTime = (seconds) => {
    if (seconds < 60) {
      return `${seconds}s`;
    }
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const PhaseIcon = PHASE_ICONS[progress.currentPhase] || Loader2;

  return (
    <div className="flex items-center justify-center min-h-[70vh] p-6">
      <div className="w-full max-w-2xl">
        {/* Main Progress Header */}
        <div className="text-center mb-8">
          <div className="relative w-32 h-32 mx-auto mb-6">
            {/* Circular Progress */}
            <svg className="w-32 h-32 transform -rotate-90">
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="#e2e8f0"
                strokeWidth="8"
                fill="none"
              />
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="url(#multiProgressGradient)"
                strokeWidth="8"
                fill="none"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 56}`}
                strokeDashoffset={`${2 * Math.PI * 56 * (1 - progress.overallProgress / 100)}`}
                className="transition-all duration-500"
              />
              <defs>
                <linearGradient id="multiProgressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="50%" stopColor="#8b5cf6" />
                  <stop offset="100%" stopColor="#06b6d4" />
                </linearGradient>
              </defs>
            </svg>
            
            {/* Center Content */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-bold text-slate-800">
                {Math.round(progress.overallProgress)}%
              </span>
              <span className="text-xs text-slate-500">
                {progress.currentStep}/{progress.totalSteps}
              </span>
            </div>
          </div>

          {/* Current Status */}
          <h2 className="text-xl font-semibold text-slate-800 mb-2">
            {progress.isComplete ? 'All Processes Generated!' : 
             progress.isError ? 'Generation Failed' :
             `Generating Process ${progress.currentStep} of ${progress.totalSteps}`}
          </h2>
          
          <p className="text-slate-500 mb-4">
            {progress.currentMessage}
          </p>

          {/* Time Estimate */}
          {!progress.isComplete && !progress.isError && (
            <div className="flex items-center justify-center gap-4 text-sm">
              <div className="flex items-center gap-1 text-slate-400">
                <Clock className="w-4 h-4" />
                <span>Elapsed: {formatTime(progress.elapsedSeconds)}</span>
              </div>
              <div className="flex items-center gap-1 text-blue-500">
                <Clock className="w-4 h-4" />
                <span>~{formatTime(progress.estimatedRemainingSeconds)} remaining</span>
              </div>
            </div>
          )}
        </div>

        {/* Process List */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
            <h3 className="font-medium text-slate-700">Processes</h3>
          </div>
          
          <div className="divide-y divide-slate-100">
            {processTitles.map((title, index) => {
              const isCompleted = index < progress.currentStep;
              const isCurrent = index === progress.currentStep - 1;
              const isPending = index >= progress.currentStep;
              
              // Find completed step data
              const completedData = progress.stepsCompleted?.find(
                s => s.name === title || s.processTitle === title
              );

              return (
                <div 
                  key={index}
                  className={`px-4 py-4 flex items-center gap-4 transition-all ${
                    isCurrent ? 'bg-blue-50' : ''
                  }`}
                >
                  {/* Status Icon */}
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                    isCompleted ? 'bg-green-500' :
                    isCurrent ? 'bg-blue-500' :
                    'bg-slate-200'
                  }`}>
                    {isCompleted ? (
                      <CheckCircle className="w-5 h-5 text-white" />
                    ) : isCurrent ? (
                      <Loader2 className="w-5 h-5 text-white animate-spin" />
                    ) : (
                      <span className="text-sm font-medium text-slate-500">{index + 1}</span>
                    )}
                  </div>

                  {/* Process Info */}
                  <div className="flex-1 min-w-0">
                    <p className={`font-medium truncate ${
                      isCompleted ? 'text-green-700' :
                      isCurrent ? 'text-blue-700' :
                      'text-slate-400'
                    }`}>
                      {title}
                    </p>
                    
                    {isCurrent && (
                      <div className="mt-2">
                        <div className="flex items-center gap-2 text-xs text-blue-600 mb-1">
                          <PhaseIcon className="w-3 h-3" />
                          <span>{PHASE_LABELS[progress.currentPhase] || progress.currentPhase}</span>
                        </div>
                        <div className="h-1.5 bg-blue-100 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-500 rounded-full transition-all duration-300"
                            style={{ width: `${progress.subProgress || 0}%` }}
                          />
                        </div>
                      </div>
                    )}
                    
                    {isCompleted && completedData && (
                      <p className="text-xs text-green-600 mt-1">
                        ✓ {completedData.nodes || completedData.nodeCount || '?'} nodes generated
                      </p>
                    )}
                  </div>

                  {/* Status Badge */}
                  <div className="flex-shrink-0">
                    {isCompleted && (
                      <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded">
                        Done
                      </span>
                    )}
                    {isCurrent && (
                      <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded">
                        In Progress
                      </span>
                    )}
                    {isPending && !isCurrent && (
                      <span className="text-xs font-medium text-slate-400">
                        Pending
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Connection Status */}
        <div className="mt-4 text-center">
          <span className={`text-xs ${
            connectionStatus === 'connected' ? 'text-green-500' :
            connectionStatus === 'reconnecting' ? 'text-yellow-500' :
            connectionStatus === 'error' ? 'text-red-500' :
            'text-slate-400'
          }`}>
            {connectionStatus === 'connected' && '● Live updates active'}
            {connectionStatus === 'connecting' && '○ Connecting...'}
            {connectionStatus === 'reconnecting' && '○ Reconnecting...'}
            {connectionStatus === 'completed' && '● Completed'}
            {connectionStatus === 'error' && '● Connection lost'}
          </span>
        </div>

        {/* Footer Tip */}
        <p className="text-center text-xs text-slate-400 mt-6">
          💡 Complex documents with multiple processes take longer to analyze accurately
        </p>
      </div>
    </div>
  );
};

export default MultiProcessProgress;
