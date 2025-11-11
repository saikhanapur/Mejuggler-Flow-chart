import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, Share2, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import FlowchartDisplay from './FlowchartDisplay';
import OperationalDetailsPanel from '../OperationalDetailsPanel';
import ExportModal from '../ExportModal';
import ShareModal from '../ShareModal';
import AIRefineChat from '../AIRefineChat';
import { api } from '@/utils/api';
import { toast } from 'sonner';

const FlowchartCanvas = ({ processData }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [process, setProcess] = useState(processData || null);
  const [loading, setLoading] = useState(!processData);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [showAIChat, setShowAIChat] = useState(false);

  useEffect(() => {
    if (!processData) {
      loadProcess();
    }
  }, [id]);

  const loadProcess = async () => {
    try {
      setLoading(true);
      const data = await api.getProcess(id);
      setProcess(data);
    } catch (error) {
      console.error('Failed to load process:', error);
      toast.error('Failed to load flowchart');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = (node) => {
    setSelectedNode(node);
  };

  const handleUpdateNode = async (nodeId, field, value) => {
    try {
      // Call API to update node
      await api.updateProcessNode(id, nodeId, field, value);
      
      // Reload process to get updated data
      await loadProcess();
      
      // Show success message
      const fieldLabel = field === 'priority' ? 'Priority' : field === 'title' ? 'Title' : 'Description';
      toast.success(`${fieldLabel} updated successfully`);
      
      return true;
    } catch (error) {
      console.error('Failed to update node:', error);
      toast.error(`Failed to update ${field}`);
      return false;
    }
  };

  const handleExport = () => {
    setShowExportModal(true);
  };

  const handleShare = () => {
    setShowShareModal(true);
  };

  const handleAIRefine = () => {
    setShowAIChat(!showAIChat);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-600">Loading flowchart...</p>
        </div>
      </div>
    );
  }

  if (!process) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-slate-400 text-lg mb-2">Flowchart not found</div>
          <div className="text-slate-500 text-sm mb-4">The flowchart you're looking for doesn't exist.</div>
          <Button onClick={() => navigate('/')}>Go to Dashboard</Button>
        </div>
      </div>
    );
  }

  if (!process.nodes || !Array.isArray(process.nodes)) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-amber-600 text-lg mb-2">Invalid Flowchart Data</div>
          <div className="text-slate-500 text-sm mb-4">The flowchart data is malformed. Please regenerate.</div>
          <Button onClick={() => navigate('/')}>Go to Dashboard</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="sticky top-0 bg-white/80 backdrop-blur-lg border-b border-slate-200 shadow-sm z-40">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => navigate('/')}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                Back
              </Button>
              <div className="flex-1 max-w-2xl">
                <h1 className="text-xl font-bold text-slate-900 truncate">{process.name}</h1>
                {process.description && (
                  <p className="text-xs text-slate-500 mt-1 line-clamp-1">
                    {process.description}
                  </p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={handleAIRefine}
                className="flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                AI Edit
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleShare}
                className="flex items-center gap-2"
              >
                <Share2 className="w-4 h-4" />
                Share
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleExport}
                className="flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content - Side by Side Layout */}
      <div className="max-w-[1600px] mx-auto px-6 py-8 flex gap-6">
        {/* Flowchart Panel */}
        <div className="flex-1">
          <FlowchartDisplay 
            process={process} 
            onNodeClick={handleNodeClick}
            selectedNodeId={selectedNode?.id}
          />
        </div>

        {/* Step Details Panel - Fixed on Right */}
        {selectedNode && (
          <div className="w-[400px] flex-shrink-0">
            <div className="sticky top-24">
              <OperationalDetailsPanel
                node={selectedNode}
                onClose={() => setSelectedNode(null)}
              />
            </div>
          </div>
        )}
      </div>

      {/* AI Chat Panel */}
      {showAIChat && (
        <div className="fixed right-0 top-0 bottom-0 w-[480px] bg-white shadow-2xl border-l border-slate-200 z-50">
          <AIRefineChat 
            processId={id}
            onClose={() => setShowAIChat(false)}
            onUpdate={loadProcess}
          />
        </div>
      )}

      {/* Modals */}
      {showExportModal && (
        <ExportModal
          process={process}
          onClose={() => setShowExportModal(false)}
        />
      )}

      {showShareModal && (
        <ShareModal
          process={process}
          onClose={() => setShowShareModal(false)}
        />
      )}
    </div>
  );
};

export default FlowchartCanvas;
