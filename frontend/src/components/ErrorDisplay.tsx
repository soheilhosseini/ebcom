/**
 * ErrorDisplay Component
 * 
 * Displays user-friendly error messages with retry functionality.
 * Ensures no technical details are exposed to users.
 * 
 * Requirements: 11.3, 11.4, 11.5
 */

interface ErrorDisplayProps {
  /** User-friendly error message to display */
  message: string
  /** Callback to retry the failed operation */
  onRetry?: () => void
  /** Callback to dismiss the error */
  onDismiss: () => void
  /** Whether retry is available */
  canRetry?: boolean
}

/**
 * Map of common error patterns to user-friendly messages
 * Ensures technical details are not exposed (Requirement 11.5)
 */
const ERROR_MESSAGES: Record<string, string> = {
  'fetch': 'Unable to connect to the server. Please check your connection and try again.',
  'network': 'Network error occurred. Please check your internet connection.',
  'timeout': 'The request took too long. Please try again.',
  'api': 'The AI service is temporarily unavailable. Please try again later.',
  'openai': 'AI service unavailable. Please try again later.',
  'search': 'Unable to search for sources. Please try a different topic.',
  'sources': 'Could not retrieve any sources. Please try a different topic.',
}

/**
 * Sanitize error message to ensure no technical details are exposed
 * Requirement 11.5
 */
function sanitizeErrorMessage(message: string): string {
  // Check for known error patterns and return user-friendly message
  const lowerMessage = message.toLowerCase()
  
  for (const [pattern, friendlyMessage] of Object.entries(ERROR_MESSAGES)) {
    if (lowerMessage.includes(pattern)) {
      return friendlyMessage
    }
  }
  
  // Check for technical patterns that should be hidden
  const technicalPatterns = [
    /stack\s*trace/i,
    /at\s+\w+\s*\(/i,  // Stack trace line pattern
    /error\s*code:\s*\d+/i,
    /api[_-]?key/i,
    /\/[a-z]+\/[a-z]+\//i,  // File paths
    /traceback/i,
    /exception/i,
    /\b[A-Z][a-z]+Error\b/,  // Error class names like TypeError
  ]
  
  for (const pattern of technicalPatterns) {
    if (pattern.test(message)) {
      return 'An unexpected error occurred. Please try again.'
    }
  }
  
  // If message is reasonably short and doesn't contain technical details, use it
  if (message.length < 200 && !message.includes('\n')) {
    return message
  }
  
  // Default fallback
  return 'An error occurred while processing your request. Please try again.'
}

export function ErrorDisplay({
  message,
  onRetry,
  onDismiss,
  canRetry = true,
}: ErrorDisplayProps) {
  const sanitizedMessage = sanitizeErrorMessage(message)

  return (
    <div 
      className="bg-red-50 border border-red-200 rounded-xl p-6 animate-fade-in"
      role="alert"
      aria-live="assertive"
    >
      <div className="flex items-start gap-4">
        {/* Error icon */}
        <div className="flex-shrink-0">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
            <svg 
              className="w-6 h-6 text-red-600" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" 
              />
            </svg>
          </div>
        </div>

        {/* Error content */}
        <div className="flex-grow">
          <h3 className="text-lg font-semibold text-red-800 mb-1">
            Research Failed
          </h3>
          <p className="text-red-700 mb-4">
            {sanitizedMessage}
          </p>
          
          {/* Action buttons */}
          <div className="flex flex-wrap gap-3">
            {/* Retry button - Requirements 11.3, 11.4 */}
            {canRetry && onRetry && (
              <button
                onClick={onRetry}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                aria-label="Retry research"
              >
                <svg 
                  className="w-4 h-4" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
                  />
                </svg>
                Try Again
              </button>
            )}
            
            {/* Dismiss button */}
            <button
              onClick={onDismiss}
              className="px-4 py-2 text-red-600 hover:text-red-800 font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 rounded-lg"
              aria-label="Dismiss error"
            >
              Dismiss
            </button>
          </div>
        </div>
      </div>

      {/* Help text */}
      <div className="mt-4 pt-4 border-t border-red-200">
        <p className="text-sm text-red-600">
          <strong>Tips:</strong> Try using a different search topic, reducing the number of sources, 
          or checking your internet connection.
        </p>
      </div>
    </div>
  )
}
