/**
 * Error Display Components
 * Reusable components for showing user-friendly errors
 */
import React from 'react';
import { AlertCircle, XCircle, AlertTriangle, Info, RefreshCw, Mail } from 'lucide-react';

/**
 * Error severity levels
 */
export const ErrorSeverity = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  CRITICAL: 'critical'
};

/**
 * Get icon and colors for error severity
 */
const getSeverityConfig = (severity) => {
  switch (severity) {
    case ErrorSeverity.INFO:
      return {
        icon: Info,
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        textColor: 'text-blue-800',
        iconColor: 'text-blue-500'
      };
    case ErrorSeverity.WARNING:
      return {
        icon: AlertTriangle,
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
        textColor: 'text-yellow-800',
        iconColor: 'text-yellow-500'
      };
    case ErrorSeverity.ERROR:
      return {
        icon: XCircle,
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        textColor: 'text-red-800',
        iconColor: 'text-red-500'
      };
    case ErrorSeverity.CRITICAL:
      return {
        icon: AlertCircle,
        bgColor: 'bg-red-100',
        borderColor: 'border-red-300',
        textColor: 'text-red-900',
        iconColor: 'text-red-600'
      };
    default:
      return getSeverityConfig(ErrorSeverity.ERROR);
  }
};

/**
 * Main Error Display Component
 * Shows user-friendly error with actions
 */
export const ErrorDisplay = ({ error, onRetry, onClose }) => {
  // Handle both old format (string) and new format (object)
  if (typeof error === 'string') {
    error = {
      title: 'Error',
      message: error,
      severity: ErrorSeverity.ERROR,
      actions: []
    };
  }

  const {
    code,
    title,
    message,
    severity = ErrorSeverity.ERROR,
    actions = [],
    retry_available = false,
    support_contact = false,
    technical_detail
  } = error;

  const config = getSeverityConfig(severity);
  const Icon = config.icon;

  return (
    <div className={`rounded-lg border-2 ${config.borderColor} ${config.bgColor} p-6 mb-4`}>
      {/* Header */}
      <div className="flex items-start">
        <Icon className={`${config.iconColor} w-6 h-6 mr-3 flex-shrink-0 mt-0.5`} />
        <div className="flex-1">
          <h3 className={`text-lg font-semibold ${config.textColor} mb-2`}>
            {title}
          </h3>
          <p className={`${config.textColor} mb-4`}>
            {message}
          </p>

          {/* Action Items */}
          {actions && actions.length > 0 && (
            <div className="mb-4">
              <p className={`text-sm font-medium ${config.textColor} mb-2`}>
                What you can do:
              </p>
              <ul className={`text-sm ${config.textColor} space-y-1 ml-4`}>
                {actions.map((action, index) => (
                  <li key={index} className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>{action}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Buttons */}
          <div className="flex flex-wrap gap-3 mt-4">
            {retry_available && onRetry && (
              <button
                onClick={onRetry}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </button>
            )}

            {support_contact && (
              <a
                href="mailto:support@superhumanly.ai"
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Mail className="w-4 h-4 mr-2" />
                Contact Support
              </a>
            )}

            {onClose && (
              <button
                onClick={onClose}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                Close
              </button>
            )}
          </div>

          {/* Technical Details (collapsible) */}
          {technical_detail && (
            <details className="mt-4">
              <summary className={`text-sm ${config.textColor} cursor-pointer hover:underline`}>
                Technical Details (for support)
              </summary>
              <pre className={`mt-2 text-xs ${config.textColor} bg-white bg-opacity-50 p-2 rounded overflow-auto max-h-32`}>
                {technical_detail}
              </pre>
            </details>
          )}

          {/* Error Code */}
          {code && (
            <p className={`text-xs ${config.textColor} opacity-60 mt-2`}>
              Error Code: {code}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Inline Error - Smaller, less prominent
 */
export const InlineError = ({ message, className = '' }) => {
  return (
    <div className={`flex items-center text-red-600 text-sm ${className}`}>
      <XCircle className="w-4 h-4 mr-2 flex-shrink-0" />
      <span>{message}</span>
    </div>
  );
};

/**
 * Warning Display - For non-critical warnings
 */
export const WarningDisplay = ({ title, message, onDismiss }) => {
  return (
    <div className="rounded-lg border-2 border-yellow-200 bg-yellow-50 p-4 mb-4">
      <div className="flex items-start">
        <AlertTriangle className="text-yellow-500 w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          {title && (
            <h4 className="text-sm font-semibold text-yellow-800 mb-1">
              {title}
            </h4>
          )}
          <p className="text-sm text-yellow-700">
            {message}
          </p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-yellow-600 hover:text-yellow-800 ml-2"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
};

/**
 * Error Modal - Full screen overlay for critical errors
 */
export const ErrorModal = ({ error, onRetry, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-auto shadow-2xl">
        <div className="p-6">
          <ErrorDisplay error={error} onRetry={onRetry} onClose={onClose} />
        </div>
      </div>
    </div>
  );
};

/**
 * Toast Notification - Brief error notification
 */
export const ErrorToast = ({ message, onClose }) => {
  React.useEffect(() => {
    const timer = setTimeout(() => {
      if (onClose) onClose();
    }, 5000);
    
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed bottom-4 right-4 z-50 animate-slide-up">
      <div className="bg-red-50 border-2 border-red-200 rounded-lg shadow-lg p-4 max-w-md">
        <div className="flex items-start">
          <XCircle className="text-red-500 w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm text-red-800">{message}</p>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-red-600 hover:text-red-800 ml-2 text-xl leading-none"
            >
              ×
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Loading with potential timeout warning
 */
export const LoadingWithTimeout = ({ timeoutSeconds = 60, onTimeout }) => {
  const [elapsed, setElapsed] = React.useState(0);
  const [showWarning, setShowWarning] = React.useState(false);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(prev => {
        const next = prev + 1;
        if (next > timeoutSeconds * 0.75 && !showWarning) {
          setShowWarning(true);
        }
        if (next >= timeoutSeconds && onTimeout) {
          onTimeout();
        }
        return next;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [timeoutSeconds, onTimeout, showWarning]);

  return (
    <div className="text-center">
      <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
      <p className="text-gray-600">Processing... ({elapsed}s)</p>
      {showWarning && (
        <p className="text-yellow-600 text-sm mt-2">
          This is taking longer than expected. Please wait...
        </p>
      )}
    </div>
  );
};

export default ErrorDisplay;
