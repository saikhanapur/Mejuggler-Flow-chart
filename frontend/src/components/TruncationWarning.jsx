/**
 * Truncation Warning Modal
 * Shows when uploaded document exceeds character limit
 */
import React from 'react';
import { AlertTriangle, FileText, Scissors } from 'lucide-react';
import { Button } from '@/components/ui/button';

const TruncationWarning = ({ 
  originalLength, 
  truncatedLength = 100000,
  onProceed, 
  onCancel 
}) => {
  // Calculate approximate pages (assuming ~2500 chars per page)
  const originalPages = Math.ceil(originalLength / 2500);
  const truncatedPages = Math.ceil(truncatedLength / 2500);
  const percentageKept = Math.round((truncatedLength / originalLength) * 100);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-lg w-full shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-amber-50 border-b border-amber-200 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-amber-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-amber-900">
                Document Exceeds Limit
              </h2>
              <p className="text-sm text-amber-700">
                Your document is larger than we can process in one go
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-5 space-y-4">
          {/* Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 rounded-lg p-4 text-center">
              <FileText className="w-6 h-6 text-slate-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-slate-800">~{originalPages}</div>
              <div className="text-xs text-slate-500">pages uploaded</div>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <Scissors className="w-6 h-6 text-blue-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-blue-600">~{truncatedPages}</div>
              <div className="text-xs text-blue-500">pages will be processed</div>
            </div>
          </div>

          {/* Explanation */}
          <div className="bg-slate-50 rounded-lg p-4">
            <p className="text-sm text-slate-700 leading-relaxed">
              We'll process the <strong>first {truncatedPages} pages</strong> ({percentageKept}% of your document). 
              The flowchart will be based on this portion only.
            </p>
          </div>

          {/* Tips */}
          <div className="text-sm text-slate-600">
            <p className="font-medium mb-2">💡 For best results with long documents:</p>
            <ul className="space-y-1 ml-4 text-slate-500">
              <li>• Split into smaller sections by topic</li>
              <li>• Upload each section separately</li>
              <li>• Remove appendices or reference sections</li>
            </ul>
          </div>
        </div>

        {/* Actions */}
        <div className="bg-slate-50 px-6 py-4 flex gap-3 border-t">
          <Button
            onClick={onCancel}
            variant="outline"
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            onClick={onProceed}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
          >
            Process First {truncatedPages} Pages →
          </Button>
        </div>
      </div>
    </div>
  );
};

export default TruncationWarning;
