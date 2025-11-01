import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '@/utils/api';
import { ArrowLeft, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';

const HTMLFlowchartViewer = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [html, setHtml] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadHTMLFlowchart();
  }, [id]);

  const loadHTMLFlowchart = async () => {
    try {
      const data = await api.getHTMLFlowchart(id);
      setHtml(data.html);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load HTML flowchart:', err);
      setError('Failed to load flowchart');
      setLoading(false);
    }
  };

  const openInNewTab = () => {
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-600">Loading flowchart...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={() => navigate('/dashboard')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top Bar */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
          
          <Button
            onClick={openInNewTab}
            className="flex items-center gap-2"
          >
            <ExternalLink className="w-4 h-4" />
            Open in New Tab
          </Button>
        </div>
      </div>

      {/* HTML Content - Full Screen */}
      <div className="w-full h-[calc(100vh-73px)]">
        <iframe
          srcDoc={html}
          title="Interactive Flowchart"
          className="w-full h-full border-0"
          sandbox="allow-scripts allow-same-origin"
        />
      </div>
    </div>
  );
};

export default HTMLFlowchartViewer;
