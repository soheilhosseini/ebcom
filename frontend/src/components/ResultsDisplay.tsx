import ReactMarkdown from 'react-markdown'

interface ResultsDisplayProps {
  result: string
  format: 'json' | 'markdown'
  onCopy: () => void
  onDownload: () => void
  copySuccess: boolean
}

/**
 * ResultsDisplay Component
 * 
 * Displays research results in a single-column scrollable layout.
 * Renders Markdown with react-markdown or JSON in formatted code block.
 * Makes citation URLs clickable.
 * 
 * Requirements: 9.1, 9.2, 9.3, 9.4
 */
export function ResultsDisplay({
  result,
  format,
  onCopy,
  onDownload,
  copySuccess,
}: ResultsDisplayProps) {
  /**
   * Custom link renderer to make URLs clickable
   * Opens links in new tab with security attributes
   */
  const LinkRenderer = ({ href, children }: { href?: string; children?: React.ReactNode }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-blue-600 hover:text-blue-800 underline break-all"
    >
      {children}
    </a>
  )

  /**
   * Format JSON for display with syntax highlighting
   */
  const formatJSON = (jsonString: string): string => {
    try {
      const parsed = JSON.parse(jsonString)
      return JSON.stringify(parsed, null, 2)
    } catch {
      // If parsing fails, return as-is
      return jsonString
    }
  }

  return (
    <div className="space-y-4">
      {/* Header with export buttons */}
      <div className="flex items-center justify-between border-b border-gray-200 pb-4">
        <h2 className="text-xl font-semibold text-gray-800">
          Research Results
        </h2>
        <div className="flex gap-2">
          {/* Copy to clipboard button - Requirements 10.1, 10.2 */}
          <button
            onClick={onCopy}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              copySuccess
                ? 'bg-green-100 text-green-700 border border-green-300'
                : 'bg-gray-100 hover:bg-gray-200 text-gray-700 border border-gray-300'
            }`}
            title="Copy to clipboard"
          >
            {copySuccess ? (
              <>
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Copied!
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy
              </>
            )}
          </button>

          {/* Download button - Requirements 10.3, 10.4, 10.5, 10.6 */}
          <button
            onClick={onDownload}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            title={`Download as ${format === 'markdown' ? '.md' : '.json'} file`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download {format === 'markdown' ? '.md' : '.json'}
          </button>
        </div>
      </div>

      {/* Results content - Requirement 9.1: Single-column scrollable layout */}
      <div className="max-h-[600px] overflow-y-auto">
        {format === 'markdown' ? (
          /* Markdown rendering - Requirements 9.2, 9.4 */
          <div className="prose prose-sm sm:prose lg:prose-lg max-w-none prose-headings:text-gray-800 prose-p:text-gray-700 prose-li:text-gray-700 prose-a:text-blue-600 prose-a:no-underline hover:prose-a:underline prose-code:bg-gray-100 prose-code:px-1 prose-code:rounded prose-pre:bg-gray-900 prose-pre:text-gray-100">
            <ReactMarkdown
              components={{
                a: LinkRenderer,
              }}
            >
              {result}
            </ReactMarkdown>
          </div>
        ) : (
          /* JSON rendering - Requirements 9.3, 9.4 */
          <div className="relative">
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono">
              <code>{formatJSON(result)}</code>
            </pre>
          </div>
        )}
      </div>

      {/* Format indicator */}
      <div className="text-right text-sm text-gray-500">
        Format: {format === 'markdown' ? 'Markdown' : 'JSON'}
      </div>
    </div>
  )
}
