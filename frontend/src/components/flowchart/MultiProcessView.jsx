/**
 * Multi-Process View Component
 * 
 * Displays multiple flowcharts side-by-side in a single view.
 * Perfect for multi-instance processes (e.g., Panic/Silent/Missed Checkin alerts)
 */

import React, { useState } from 'react';
import { ReactFlowChart } from './ReactFlowChart';
import { ArrowLeft, Maximize2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

const MultiProcessView = ({ processes, onBack, onProcessClick }) => {
  const [selectedProcess, setSelectedProcess] = useState(null);
  
  if (selectedProcess) {
    // Full-screen single process view
    return (
      <div className="h-screen flex flex-col">
        <div className="bg-white border-b px-6 py-4 flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={() => setSelectedProcess(null)}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to All Processes
          </Button>
          <h2 className="text-xl font-semibold">{selectedProcess.name}</h2>
          <div className="w-32" /> {/* Spacer for centering */}
        </div>
        
        <div className="flex-1 bg-gray-50">
          <ReactFlowChart 
            processData={selectedProcess}
            onNodeClick={(node) => console.log('Node clicked:', node)}
          />
        </div>
      </div>
    );
  }
  
  // Multi-view grid layout
  const gridClass = processes.length === 2 
    ? 'grid-cols-2' 
    : processes.length === 3 
    ? 'grid-cols-3' 
    : 'grid-cols-2';
  
  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between max-w-[1800px] mx-auto">
          <Button
            variant="ghost"
            onClick={onBack}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
          
          <div className="text-center">
            <h1 className="text-2xl font-bold">Multi-Process View</h1>
            <p className="text-sm text-gray-600">{processes.length} Processes</p>
          </div>
          
          <div className="w-24" /> {/* Spacer */}
        </div>
      </div>
      
      {/* Grid of Flowcharts */}
      <div className={`flex-1 p-6 grid ${gridClass} gap-6 max-w-[1800px] mx-auto w-full`}>
        {processes.map((process, index) => (
          <div 
            key={process.id || index}
            className="bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden flex flex-col"
          >
            {/* Process Header */}
            <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-4 py-3 flex items-center justify-between">
              <h3 className="font-semibold text-lg">{process.name || `Process ${index + 1}`}</h3>
              <Button
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/20"
                onClick={() => setSelectedProcess(process)}
              >
                <Maximize2 className="w-4 h-4" />
              </Button>
            </div>
            
            {/* Process Stats */}
            <div className="px-4 py-2 bg-gray-50 border-b flex gap-4 text-xs">
              <span className="text-gray-600">
                {process.nodes?.length || 0} nodes
              </span>
              <span className="text-gray-600">
                {process.nodes?.filter(n => n.isDecisionPoint).length || 0} decisions
              </span>
            </div>
            
            {/* Flowchart */}
            <div className="flex-1 min-h-0">
              <ReactFlowChart 
                processData={process}
                onNodeClick={(node) => {
                  console.log('Node clicked in multi-view:', node);
                  if (onProcessClick) {
                    onProcessClick(process.id, node);
                  }
                }}
              />
            </div>
          </div>
        ))}
      </div>
      
      {/* Tip */}
      <div className="bg-blue-50 border-t border-blue-200 px-6 py-3 text-center">
        <p className="text-sm text-blue-800">
          💡 <strong>Tip:</strong> Click the maximize icon on any process to view it in full screen
        </p>
      </div>
    </div>
  );
};

export default MultiProcessView;
