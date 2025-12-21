import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mic, Upload, MessageSquare, ArrowLeft, CheckCircle, AlertCircle, FolderOpen, Sparkles, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import VoiceRecorder from './VoiceRecorder';
import DocumentUploader from './DocumentUploader';
import ChatInterface from './ChatInterface';
import MultiProcessReview from './MultiProcessReview';
import ContextAdder from './ContextAdder';
import SmartQuestionPanel from './SmartQuestionPanel';
import LiveProgressPanel from './LiveProgressPanel';
import DocumentAnalysisReview from './DocumentAnalysisReview';
import CoverageReportPanel from './CoverageReportPanel';
import DynamicLoadingScreen from './DynamicLoadingScreen';
import ExtractionReview from './ExtractionReview';
import { ErrorDisplay } from './ErrorDisplay';
import { api } from '@/utils/api';
import { streamDocumentAnalysis } from '@/utils/sseClient';
import { toast } from 'sonner';

const ProcessCreator = ({ currentWorkspace, isGuestMode = false }) => {
  const navigate = useNavigate();
  const [method, setMethod] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState(''); // Track processing step
  const [extractedText, setExtractedText] = useState(null);
  const [showContextAdder, setShowContextAdder] = useState(false);
  const [extractedData, setExtractedData] = useState(null);
  
  // Error handling state
  const [processingError, setProcessingError] = useState(null);
  
  // Smart question flow with streaming
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [showSmartQuestions, setShowSmartQuestions] = useState(false);
  const [contextAnswers, setContextAnswers] = useState(null);
  
  // Streaming progress
  const [progressUpdates, setProgressUpdates] = useState([]);
  const [showLiveProgress, setShowLiveProgress] = useState(false);
  const sseConsumerRef = useRef(null);
  
  // Predictive pre-loading
  const [preloadedAnalysis, setPreloadedAnalysis] = useState(null);
  
  // Superintelligent AI Pipeline
  const [useSuperintelligent, setUseSuperintelligent] = useState(false);
  const [documentAnalysis, setDocumentAnalysis] = useState(null);
  const [showAnalysisReview, setShowAnalysisReview] = useState(false);
  const [coverageReport, setCoverageReport] = useState(null);
  const [showCoverageReport, setShowCoverageReport] = useState(false);
  
  // Project selection (disabled in guest mode)
  const [workspaces, setWorkspaces] = useState([]);
  const [selectedWorkspace, setSelectedWorkspace] = useState(null);
  
  // Parse structured error from backend API responses
  const parseBackendError = (err) => {
    if (err.response?.data?.detail) {
      const detail = err.response.data.detail;
      if (typeof detail === 'object' && detail.code) {
        return detail;
      }
      if (typeof detail === 'string') {
        return {
          title: 'Processing Failed',
          message: detail,
          severity: 'error',
          actions: ['Try a different document', 'Simplify your document content'],
          retry_available: true
        };
      }
    }
    // Fallback for generic errors
    const errorMessage = err.message || 'An unexpected error occurred';
    return {
      title: 'Error',
      message: errorMessage,
      severity: 'error',
      actions: ['Try again', 'Contact support if the issue persists'],
      retry_available: true
    };
  };

  useEffect(() => {
    if (!isGuestMode) {
      loadWorkspaces();
    }
  }, [isGuestMode]);

  const loadWorkspaces = async () => {
    try {
      const data = await api.getWorkspaces();
      setWorkspaces(data);
      if (currentWorkspace) {
        setSelectedWorkspace(currentWorkspace.id);
      } else if (data.length > 0) {
        setSelectedWorkspace(data[0].id);
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
    }
  };

  const handleInputComplete = async (input, inputType) => {
    // For documents, use EXTRACTION FIRST, then generate flowchart after review
    if (inputType === 'document') {
      setExtractedText(input);
      setProcessing(true);
      setProcessingStep('🔍 Extracting intelligence from document...');
      
      try {
        // STEP 1: Extract intelligence ONLY (no flowchart generation yet)
        const extractionResult = await api.extractDocumentIntelligence(input, inputType);
        
        console.log('=== EXTRACTION RESULT ===');
        console.log('Extraction:', JSON.stringify(extractionResult, null, 2));
        
        if (!extractionResult.success) {
          throw new Error('Extraction failed');
        }
        
        // Show extraction review modal
        setDocumentAnalysis(extractionResult.extraction);
        setShowAnalysisReview(true);
        setProcessing(false);
        
        // Wait for user confirmation before generating flowchart
        return;
        
      } catch (error) {
        console.error('Extraction failed:', error);
        toast.error('Failed to extract document intelligence');
        setProcessing(false);
        return;
      }
    }
    
    // For non-documents, proceed directly
    handleFlowchartGeneration(input, inputType);
  };
  
  const handleFlowchartGeneration = async (input, inputType) => {
    setProcessing(true);
    setProcessingStep('Creating intelligent flowchart...');
    
    try {
      // Using proven EROAD service with intelligent 10-15 node grouping
      // ⚡ Use Lightning Mode for fast, reliable generation
      const result = await api.generateLightningFlowchart(input, inputType);
        
        console.log('=== GENERATION RESULT ===');
        console.log('Full result:', JSON.stringify(result, null, 2));
        console.log('multipleProcesses:', result.multipleProcesses);
        console.log('processCount:', result.processCount);
        console.log('processTitles:', result.processTitles);
        console.log('processes array length:', result.processes?.length);
        
        // VALIDATION: Check response structure
        if (!result) {
          throw new Error('No response from server');
        }
        
        // Check if multiple processes detected
        if (result.multipleProcesses) {
          console.log(`✅ Multiple processes detected: ${result.processCount || result.detectedProcessCount}`);
          
          // HANDLE MULTIPLE RESPONSE FORMATS
          // Backend might return processTitles OR processes array
          let processTitles = result.processTitles;
          
          // If processTitles missing but processes array exists, extract titles
          if ((!processTitles || processTitles.length === 0) && result.processes && Array.isArray(result.processes)) {
            console.log('📋 Extracting process titles from processes array');
            processTitles = result.processes.map(p => p.name || p.title || p.processName || 'Unnamed Process');
            result.processTitles = processTitles;
            result.processCount = processTitles.length;
          }
          
          // VALIDATION: Ensure we have processTitles after extraction
          if (!processTitles || !Array.isArray(processTitles) || processTitles.length === 0) {
            console.error('❌ Multi-process detected but no process information found');
            console.error('Backend response:', result);
            throw new Error('Invalid multi-process detection: Could not extract process titles. Please try again.');
          }
          
          console.log(`✅ Valid multi-process with titles:`, processTitles);
          
          console.log(`✅ Setting extracted data with ${result.processTitles.length} processes`);
          
          // Build extractedData with all required fields and defaults
          const extractedData = {
            text: input,
            inputType: inputType,
            multipleProcesses: true,
            processCount: result.processCount || result.processTitles.length,
            processTitles: result.processTitles,
            processDescriptions: result.processDescriptions || result.processTitles.map(() => ''),
            recommendation: result.recommendation || 'multiple_flowcharts',
            complexity: result.complexity || 'unknown',
            reasoning: result.reasoning || 'Multiple distinct processes detected',
            autoDecision: result.autoDecision || 'Create each process as a separate flowchart',
            detection: result.detection || {}
          };
          
          console.log('✅ Extracted data prepared:', extractedData);
          
          setExtractedData(extractedData);
          setProcessing(false);
          toast.info(`${result.processCount} processes detected in document!`);
          
          console.log('✅ State updated, should show MultiProcessReview');
          return;
        }
        
        // Single process - validate and create it
        if (!result.processes || result.processes.length === 0) {
          throw new Error('No flowchart generated. Please try a different document.');
        }
        
        const process = result.processes[0];
        
        // Validate
        if (!process.name || !process.nodes) {
          throw new Error('Invalid process structure');
        }
        
        const processData = {
          ...process,
          workspaceId: selectedWorkspace,
          userId: null,
          isGuest: isGuestMode
        };
        
        console.log('Creating process:', processData);
        
        const createdProcess = await api.createProcess(processData);
        
        setProcessing(false);
        toast.success('Flowchart created successfully!');
        
        // Navigate to editor
        const editRoute = isGuestMode ? `/guest-edit/${createdProcess.id}` : `/edit/${createdProcess.id}`;
        setTimeout(() => {
          navigate(editRoute);
        }, 1000);
        
      } catch (error) {
        console.error('Generation failed:', error);
        const parsedError = parseBackendError(error);
        setProcessingError(parsedError);
        setProcessing(false);
      }
  };

  const handleAnalysisApproved = async ({ approvedSections, corrections }) => {
    setShowAnalysisReview(false);
    setProcessing(true);
    setProcessingStep('Generating flowchart from approved analysis...');
    
    try {
      // Stages 1-3: Generate flowchart from approved analysis
      const result = await api.generateFromAnalysis(
        extractedText,
        documentAnalysis.analysisId,
        approvedSections,
        corrections
      );
      
      console.log('Generation result:', result); // Debug log
      
      // Check if we have processes
      if (!result.processes || result.processes.length === 0) {
        throw new Error('No processes returned from analysis');
      }
      
      // Check if multiple processes detected
      if (result.multipleProcesses && result.processes.length > 1) {
        setExtractedData(result);
        setProcessing(false);
        // Show multi-process review (existing component)
        return;
      }
      
      // Single process - create it
      const process = result.processes[0];
      
      // Validate process has required fields
      if (!process.processName && !process.name) {
        throw new Error('Process missing name field');
      }
      if (!process.nodes) {
        throw new Error('Process missing nodes');
      }
      
      // Map processName to name (backend expects 'name', AI returns 'processName')
      const processData = {
        ...process,
        name: process.processName || process.name, // Map processName → name
        workspaceId: selectedWorkspace,
        userId: null, // Will be set by backend if authenticated
        isGuest: isGuestMode
      };
      
      // Remove processName if it exists (avoid duplicate fields)
      delete processData.processName;
      
      console.log('Creating process with data:', processData); // Debug log
      
      const createdProcess = await api.createProcess(processData);
      
      // Show coverage report
      if (result.coverageReport) {
        setCoverageReport(result.coverageReport);
        setShowCoverageReport(true);
      }
      
      setProcessing(false);
      toast.success('Flowchart created successfully!');
      
      // Navigate to the flowchart
      // Use /edit/:id for authenticated users, /guest-edit/:id for guests
      const editRoute = isGuestMode ? `/guest-edit/${createdProcess.id}` : `/edit/${createdProcess.id}`;
      setTimeout(() => {
        navigate(editRoute);
      }, 1500);
      
    } catch (error) {
      console.error('Flowchart generation failed:', error);
      const parsedError = parseBackendError(error);
      setProcessingError(parsedError);
      setProcessing(false);
    }
  };

  const handleAnalysisCancelled = () => {
    setShowAnalysisReview(false);
    setDocumentAnalysis(null);
    setExtractedText(null);
  };

  const analyzeDocumentWithStreaming = async (text, inputType) => {
    setAnalyzing(true);
    setShowLiveProgress(true);
    setProgressUpdates([]);
    
    try {
      const consumer = streamDocumentAnalysis(text, {
        onProgress: (data) => {
          setProgressUpdates(prev => [...prev, data]);
        },
        onComplete: (data) => {
          setAnalysis(data);
          setShowLiveProgress(false);
          handleAnalysisComplete(data, text, inputType);
        },
        onError: (error) => {
          console.error('Streaming analysis failed:', error);
          toast.error('Analysis failed, trying fallback...');
          // Fallback to regular API
          analyzeDocumentFallback(text, inputType);
        }
      });
      
      sseConsumerRef.current = consumer;
      
    } catch (error) {
      console.error('Failed to start streaming:', error);
      analyzeDocumentFallback(text, inputType);
    } finally {
      setAnalyzing(false);
    }
  };

  const analyzeDocumentFallback = async (text, inputType) => {
    // 🎯 Using NEW Actionable Intelligence Service for comprehensive extraction
    try {
      console.log('🎯 Using Actionable Intelligence Service...');
      const comprehensiveResult = await api.analyzeDocumentComprehensive(text, inputType);
      
      // Transform to expected format for compatibility
      const analysisResult = {
        is_multi_process: comprehensiveResult.multipleProcesses || false,
        process_count: comprehensiveResult.processes?.length || 1,
        process_type: comprehensiveResult.processes?.[0]?.type || 'business_continuity',
        detected_steps: comprehensiveResult.processes?.[0]?.nodes?.length || 0,
        complexity: comprehensiveResult.processes?.[0]?.nodes?.length > 20 ? 'complex' : 'moderate',
        metadata: comprehensiveResult.metadata,
        validation: comprehensiveResult.validation
      };
      
      console.log('✅ Comprehensive extraction complete:', {
        nodes: analysisResult.detected_steps,
        completeness: comprehensiveResult.validation?.completeness_score
      });
      
      setAnalysis(analysisResult);
      setShowLiveProgress(false);
      handleAnalysisComplete(analysisResult, text, inputType, comprehensiveResult);
    } catch (error) {
      console.error('❌ Comprehensive analysis failed, falling back to simple:', error);
      // Fallback to old simple service if comprehensive fails
      try {
        const analysisResult = await api.analyzeDocument(text, inputType);
        setAnalysis(analysisResult);
        setShowLiveProgress(false);
        handleAnalysisComplete(analysisResult, text, inputType);
      } catch (fallbackError) {
        setAnalyzing(false);
        setShowLiveProgress(false);
        toast.error('Analysis failed. Please try again.');
      }
    }
  };

  const handleAnalysisComplete = (analysisResult, text, inputType, comprehensiveResult = null) => {
    setAnalyzing(false);
    
    // Show success toast with completeness score if available
    const completenessInfo = comprehensiveResult?.validation?.completeness_score 
      ? ` • ${comprehensiveResult.validation.completeness_score}% complete`
      : '';
    
    toast.success(
      <div>
        <div className="font-semibold">✨ Analysis Complete!</div>
        <div className="text-sm text-slate-600 mt-1">
          {analysisResult.is_multi_process 
            ? `${analysisResult.process_count} processes detected!`
            : `${analysisResult.process_type} • ${analysisResult.detected_steps} steps • ${analysisResult.complexity} complexity${completenessInfo}`
          }
        </div>
      </div>,
      { duration: 4000 }
    );
    
    // If we have comprehensive result, use it directly
    if (comprehensiveResult && comprehensiveResult.processes) {
      processWithComprehensiveResult(comprehensiveResult);
      return;
    }
    
    // Skip questions for multi-process documents
    if (analysisResult.is_multi_process) {
      processWithAI(text, inputType, null, null);
      return;
    }
    
    // Only show questions if complexity is medium or high
    const shouldShowQuestions = 
      (analysisResult.complexity === 'medium' || analysisResult.complexity === 'high') &&
      analysisResult.suggested_questions && 
      analysisResult.suggested_questions.length > 0;
    
    if (shouldShowQuestions) {
      setShowSmartQuestions(true);
    } else {
      processWithAI(text, inputType, null, null);
    }
  };

  const analyzeDocument = async (text, inputType) => {
    // Fast analysis with caching (non-streaming for speed)
    setAnalyzing(true);
    try {
      setProcessingStep('Analyzing your document...');
      const analysisResult = await api.analyzeDocument(text, inputType);
      setAnalysis(analysisResult);
      
      // Show engaging analysis results
      toast.success(
        <div>
          <div className="font-semibold">✨ Analysis Complete!</div>
          <div className="text-sm text-slate-600 mt-1">
            {analysisResult.is_multi_process 
              ? `${analysisResult.process_count} processes detected!`
              : `${analysisResult.process_type} • ${analysisResult.detected_steps} steps • ${analysisResult.complexity} complexity`
            }
          </div>
        </div>,
        { duration: 4000 }
      );
      
      // Skip questions for multi-process documents (they'll review each process individually)
      if (analysisResult.is_multi_process) {
        await processWithAI(text, inputType, null, null);
        return;
      }
      
      // Only show questions if complexity is medium or high AND single process
      const shouldShowQuestions = 
        (analysisResult.complexity === 'medium' || analysisResult.complexity === 'high') &&
        analysisResult.suggested_questions && 
        analysisResult.suggested_questions.length > 0;
      
      if (shouldShowQuestions) {
        setShowSmartQuestions(true);
      } else {
        // Low complexity or no questions - proceed directly
        await processWithAI(text, inputType, null, null);
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      toast.error('Analysis failed, proceeding with generation...');
      // Proceed anyway
      await processWithAI(text, inputType, null, null);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSmartQuestionsComplete = async (answers) => {
    setContextAnswers(answers);
    setShowSmartQuestions(false);
    await processWithAI(extractedText, 'document', null, answers);
  };

  const handleSkipSmartQuestions = async () => {
    setShowSmartQuestions(false);
    await processWithAI(extractedText, 'document', null, null);
  };


  const processWithComprehensiveResult = async (comprehensiveResult) => {
    // 🎯 NEW: Direct processing with comprehensive result (no additional AI calls needed)
    setProcessing(true);
    setShowContextAdder(false);
    
    try {
      console.log('🎯 Using comprehensive extraction result directly');
      
      setProcessingStep('Preparing actionable intelligence flowchart...');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // The comprehensive result is already in the format we need
      setExtractedData(comprehensiveResult);
      
      const process = comprehensiveResult.processes[0];
      const validation = comprehensiveResult.validation;
      
      toast.success(
        <div>
          <div className="font-semibold">✅ Actionable Intelligence Ready!</div>
          <div className="text-sm text-slate-600 mt-1">
            {process.nodes.length} steps • 
            {(process.resources?.contacts || []).length} contacts • 
            {(process.resources?.templates || []).length} templates • 
            {validation?.completeness_score || 0}% complete
          </div>
        </div>,
        { duration: 5000 }
      );
    } catch (error) {
      toast.error('Failed to process comprehensive result');
      console.error(error);
    } finally {
      setProcessing(false);
    }
  };

  const processWithAI = async (input, inputType, additionalContext, smartAnswers) => {
    setProcessing(true);
    setShowContextAdder(false);
    
    try {
      // Step 1: Reading
      setProcessingStep('Reading your input...');
      await new Promise(resolve => setTimeout(resolve, 500)); // Brief pause for UX
      
      // Step 2: Analyzing
      setProcessingStep('Analyzing structure and extracting steps...');
      
      const data = await api.parseProcess(input, inputType, additionalContext, smartAnswers);
      
      // Step 3: Generating
      setProcessingStep('Generating interactive flowchart...');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setExtractedData(data);
      
      // Check if multiple processes were detected
      if (data.multipleProcesses && data.processCount >= 2) {
        toast.success(`Found ${data.processCount} distinct processes in your document!`, {
          duration: 5000
        });
      } else {
        toast.success('Process captured successfully!');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to process input. Please try again or use a shorter document.');
      console.error(error);
    } finally {
      setProcessing(false);
    }
  };

  const handleContextAdded = (context) => {
    processWithAI(extractedText, 'document', context);
  };

  const handleSkipContext = () => {
    processWithAI(extractedText, 'document', null);
  };

  const handleGenerate = async () => {
    try {
      // Get first process from the array (single process case)
      const processData = extractedData.processes[0];
      
      const process = {
        id: `process-${Date.now()}`,
        name: processData.processName,
        description: processData.description || '',
        workspaceId: isGuestMode ? null : selectedWorkspace, // No workspace for guest
        nodes: processData.nodes.map((node, idx) => ({
          ...node,
          position: { x: 100, y: 100 + (idx * 150) }
        })),
        actors: processData.actors || [],
        criticalGaps: processData.criticalGaps || [],
        improvementOpportunities: processData.improvementOpportunities || [],
        status: 'draft',
        theme: 'minimalist',
        healthScore: 85,
        views: 0,
        version: 1
      };

      const created = await api.createProcess(process);
      toast.success('Process created!');
      
      // Navigate to guest-edit for guest users, regular edit for authenticated users
      if (isGuestMode) {
        navigate(`/guest-edit/${created.id}`);
      } else {
        navigate(`/edit/${created.id}`);
      }
    } catch (error) {
      // Check if guest limit reached
      if (error.response?.status === 403) {
        toast.error('Guest users can only create one flowchart. Sign up to create more!', {
          action: {
            label: 'Sign Up',
            onClick: () => navigate('/signup')
          }
        });
      } else {
        toast.error('Failed to create process');
      }
      console.error(error);
    }
  };

  // Loading screen during processing - DYNAMIC with real-time steps
  if (processing || analyzing) {
    return <DynamicLoadingScreen processingStep={processingStep} analyzing={analyzing} />;
  }

  // NEW: Show context adder after document upload (legacy, might be removed)
  if (showContextAdder && extractedText) {
    return (
      <ContextAdder
        documentText={extractedText}
        onContextAdded={handleContextAdded}
        onSkip={handleSkipContext}
      />
    );
  }

  // NEW: Show smart questions after analysis (adaptive)
  if (showSmartQuestions && analysis) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-12">
        <button 
          onClick={() => navigate('/dashboard')} 
          className="flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-8 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="font-medium">Back to Dashboard</span>
        </button>

        {/* Analysis Summary */}
        <div className="mb-6 p-6 bg-white rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-bold text-slate-900 mb-1">
                ✨ Analysis Complete
              </h2>
              <p className="text-slate-600 text-sm mb-3">
                {analysis.summary}
              </p>
              <div className="flex items-center gap-4 text-sm">
                <span className="px-3 py-1 rounded-full bg-blue-100 text-blue-700 font-medium">
                  📄 {analysis.process_type}
                </span>
                <span className="px-3 py-1 rounded-full bg-purple-100 text-purple-700 font-medium">
                  {analysis.detected_steps} steps
                </span>
                <span className={`px-3 py-1 rounded-full font-medium ${
                  analysis.complexity === 'high' ? 'bg-red-100 text-red-700' :
                  analysis.complexity === 'medium' ? 'bg-amber-100 text-amber-700' :
                  'bg-green-100 text-green-700'
                }`}>
                  {analysis.complexity} complexity
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Smart Questions */}
        <SmartQuestionPanel
          analysis={analysis}
          onComplete={handleSmartQuestionsComplete}
          onSkip={handleSkipSmartQuestions}
        />

        {/* Skip All Button */}
        <div className="mt-6 text-center">
          <button
            onClick={handleSkipSmartQuestions}
            className="text-sm text-slate-500 hover:text-slate-700 font-medium transition-colors"
          >
            Skip all questions and generate now →
          </button>
        </div>
      </div>
    );
  }

  if (extractedData) {
    // If multiple processes detected, show MultiProcessReview
    if (extractedData.multipleProcesses && extractedData.processCount >= 2) {
      return (
        <MultiProcessReview 
          processesData={extractedData}
          onBack={() => setExtractedData(null)}
          currentWorkspace={currentWorkspace}
          selectedWorkspace={selectedWorkspace}
          documentText={extractedData.text}
          inputType={extractedData.inputType}
        />
      );
    }

    // VALIDATION: Ensure we have processes array before accessing
    if (!extractedData.processes || extractedData.processes.length === 0) {
      console.error('❌ Invalid extractedData: processes array is missing or empty', extractedData);
      setExtractedData(null);
      toast.error('Invalid process data received. Please try again.');
      return null;
    }

    // Single process - show regular review
    const processData = extractedData.processes[0];
    
    return (
      <div className="max-w-4xl mx-auto px-6 py-12" data-testid="extraction-summary">
        <Card className="p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-800">
                Process Captured Successfully!
              </h2>
              <p className="text-slate-600">
                Review what we found and generate your flowchart
              </p>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-3xl font-bold text-blue-600 mb-1">
                {processData.nodes?.length || 0}
              </div>
              <div className="text-sm text-blue-800">Process Steps</div>
            </div>
            <div className="bg-emerald-50 rounded-lg p-4">
              <div className="text-3xl font-bold text-emerald-600 mb-1">
                {processData.actors?.length || 0}
              </div>
              <div className="text-sm text-emerald-800">People/Systems</div>
            </div>
            <div className="bg-rose-50 rounded-lg p-4">
              <div className="text-3xl font-bold text-rose-600 mb-1">
                {processData.criticalGaps?.length || 0}
              </div>
              <div className="text-sm text-rose-800">Critical Gaps</div>
            </div>
          </div>

          {/* Process Name */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Process Name
            </label>
            <input
              type="text"
              value={processData.processName}
              onChange={(e) => {
                const updated = {...extractedData};
                updated.processes[0].processName = e.target.value;
                setExtractedData(updated);
              }}
              className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:outline-none"
              data-testid="process-name-input"
            />
          </div>

          {/* Responsible Parties */}
          {processData.actors?.length > 0 && (
            <div className="mb-6">
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Responsible Parties
              </label>
              <div className="flex flex-wrap gap-2">
                {processData.actors.map((actor, i) => (
                  <Badge key={i} variant="secondary">{actor}</Badge>
                ))}
              </div>
            </div>
          )}

          {/* Steps Preview */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Process Steps ({processData.nodes?.length || 0})
            </label>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {processData.nodes?.map((node, i) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
                  <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">
                    {i + 1}
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-slate-800">{node.title}</div>
                    <div className="text-sm text-slate-600">{node.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Critical Gaps */}
          {processData.criticalGaps?.length > 0 && (
            <div className="mb-8">
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Critical Gaps Identified
              </label>
              <div className="space-y-2">
                {processData.criticalGaps.map((gap, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 bg-rose-50 border border-rose-200 rounded-lg">
                    <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-rose-800">{gap}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-4">
            <Button
              onClick={handleGenerate}
              className="flex-1 gradient-blue text-white"
              data-testid="generate-flowchart-btn"
            >
              Generate Flowchart →
            </Button>
            <Button
              onClick={() => setExtractedData(null)}
              variant="outline"
            >
              Start Over
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  if (!method) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-12" data-testid="method-selection">
        <Button
          onClick={() => navigate('/dashboard')}
          variant="ghost"
          className="mb-6"
          data-testid="back-to-dashboard"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Button>

        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-bold heading-font mb-6 leading-tight">
            <span className="bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
              Create an Interactive Flowchart
            </span>
          </h1>
          <p className="text-lg md:text-xl text-slate-600 max-w-2xl mx-auto mb-6">
            Choose how you'd like to document your process
          </p>
          
          {/* Project Selector */}
          {workspaces.length > 0 && (
            <div className="max-w-md mx-auto mb-6">
              <label className="block text-sm font-semibold text-slate-700 mb-2 text-left">
                Select Project
              </label>
              <Select value={selectedWorkspace} onValueChange={setSelectedWorkspace}>
                <SelectTrigger className="w-full h-12">
                  <SelectValue placeholder="Choose a project..." />
                </SelectTrigger>
                <SelectContent>
                  {workspaces.map((workspace) => (
                    <SelectItem key={workspace.id} value={workspace.id}>
                      <div className="flex items-center gap-2">
                        <FolderOpen className="w-4 h-4 text-slate-600" />
                        <span>{workspace.name}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Voice Option */}
          <Card
            className="p-8 border-2 border-slate-200 hover:border-blue-500 hover:shadow-2xl hover:shadow-blue-500/20 transition-all duration-300 cursor-pointer group relative overflow-hidden"
            onClick={() => setMethod('voice')}
            data-testid="method-voice"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-blue-200 rounded-2xl flex items-center justify-center mb-6 mx-auto group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-lg">
                <Mic className="w-10 h-10 text-blue-600" />
              </div>
              <h3 className="text-2xl font-bold text-slate-800 mb-3 text-center group-hover:text-blue-600 transition-colors">
                Voice Recording
              </h3>
              <p className="text-slate-600 text-sm leading-relaxed text-center mb-6">
                Simply explain your process out loud. Our AI will transcribe and structure it automatically.
              </p>
              <div className="text-center">
                <span className="inline-flex items-center gap-2 text-blue-600 font-semibold group-hover:gap-3 transition-all">
                  ~2-3 minutes
                  <span className="text-xl group-hover:translate-x-1 transition-transform">→</span>
                </span>
              </div>
            </div>
          </Card>

          {/* Document Option */}
          <Card
            className="p-8 border-2 border-slate-200 hover:border-emerald-500 hover:shadow-2xl hover:shadow-emerald-500/20 transition-all duration-300 cursor-pointer group relative overflow-hidden"
            onClick={() => setMethod('document')}
            data-testid="method-document"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative">
              <div className="w-20 h-20 bg-gradient-to-br from-emerald-100 to-emerald-200 rounded-2xl flex items-center justify-center mb-6 mx-auto group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-lg">
                <Upload className="w-10 h-10 text-emerald-600" />
              </div>
              <h3 className="text-2xl font-bold text-slate-800 mb-3 text-center group-hover:text-emerald-600 transition-colors">
                Upload Document
              </h3>
              <p className="text-slate-600 text-sm leading-relaxed text-center mb-6">
                Have existing documentation? Upload PDFs, Word docs, or even emails and we'll extract the process.
              </p>
              <div className="text-center">
                <span className="inline-flex items-center gap-2 text-emerald-600 font-semibold group-hover:gap-3 transition-all">
                  ~1 minute
                  <span className="text-xl group-hover:translate-x-1 transition-transform">→</span>
                </span>
              </div>
            </div>
          </Card>

          {/* Chat Option */}
          <Card
            className="p-8 border-2 border-slate-200 hover:border-amber-500 hover:shadow-2xl hover:shadow-amber-500/20 transition-all duration-300 cursor-pointer group relative overflow-hidden"
            onClick={() => setMethod('chat')}
            data-testid="method-chat"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-amber-50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative">
              <div className="w-20 h-20 bg-gradient-to-br from-amber-100 to-amber-200 rounded-2xl flex items-center justify-center mb-6 mx-auto group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-lg">
                <MessageSquare className="w-10 h-10 text-amber-600" />
              </div>
              <h3 className="text-2xl font-bold text-slate-800 mb-3 text-center group-hover:text-amber-600 transition-colors">
                Chat with AI
              </h3>
              <p className="text-slate-600 text-sm leading-relaxed text-center mb-6">
                Answer questions interactively. Our AI will guide you through documenting your process step-by-step.
              </p>
              <div className="text-center">
                <span className="inline-flex items-center gap-2 text-amber-600 font-semibold group-hover:gap-3 transition-all">
                  ~5 minutes
                  <span className="text-xl group-hover:translate-x-1 transition-transform">→</span>
                </span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <Button
        onClick={() => setMethod(null)}
        variant="ghost"
        className="mb-6"
        data-testid="change-method-btn"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Change Input Method
      </Button>

      {method === 'voice' && (
        <VoiceRecorder
          onComplete={(transcript) => handleInputComplete(transcript, 'voice_transcript')}
          onCancel={() => setMethod(null)}
        />
      )}

      {method === 'document' && (
        <DocumentUploader
          onComplete={(text) => handleInputComplete(text, 'document')}
          onCancel={() => setMethod(null)}
        />
      )}

      {method === 'chat' && (
        <ChatInterface
          onComplete={(conversation) => handleInputComplete(conversation, 'chat')}
          onCancel={() => setMethod(null)}
        />
      )}

      {/* Superintelligent AI: Document Analysis Review Modal */}
      {showAnalysisReview && documentAnalysis && (
        <ExtractionReview
          extractionData={documentAnalysis}
          onConfirm={() => {
            setShowAnalysisReview(false);
            handleFlowchartGeneration(extractedText, 'document');
          }}
          onCancel={() => {
            setShowAnalysisReview(false);
            setProcessing(false);
            toast.info('Flowchart generation cancelled');
          }}
          isProcessing={processing}
        />
      )}

      {/* Superintelligent AI: Coverage Report Panel */}
      {coverageReport && (
        <CoverageReportPanel
          coverageReport={coverageReport}
          isOpen={showCoverageReport}
          onToggle={() => setShowCoverageReport(!showCoverageReport)}
        />
      )}
    </div>
  );
};

export default ProcessCreator;
