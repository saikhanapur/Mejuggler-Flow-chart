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

  const activeStatus = statuses[currentStatus];

  return (
    <div className="flex items-center justify-center min-h-[80vh] p-6">
      <div className="w-full max-w-lg">
        {/* Clean, Simple Loading */}
        <div className="text-center">
          {/* Large animated icon */}
          <div className="mb-8 relative">
            <div className="w-24 h-24 mx-auto">
              <div className="absolute inset-0 border-4 border-indigo-200 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-4xl animate-pulse">{activeStatus.icon}</span>
              </div>
            </div>
          </div>
          
          {/* Status text */}
          <h2 className="text-2xl font-bold text-slate-800 mb-3 animate-pulse">
            {activeStatus.text}
          </h2>
          
          <p className="text-slate-600 mb-8">
            Creating your interactive flowchart
          </p>

          {/* Progress bar */}
          <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
            <div 
              className={`h-2 rounded-full transition-all duration-1000 bg-gradient-to-r from-${activeStatus.color}-500 to-${activeStatus.color}-600`}
              style={{ 
                width: `${((currentStatus + 1) / statuses.length) * 100}%`,
                animation: 'pulse 2s ease-in-out infinite'
              }}
            ></div>
          </div>

          {/* Subtle hint */}
          <p className="text-xs text-slate-400 mt-6">
            This typically takes 1-2 minutes
          </p>
        </div>
      </div>
    </div>
  );
};

export default DynamicLoadingScreen;
