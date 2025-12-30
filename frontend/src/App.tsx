import { useState, useCallback } from 'react'
import { InputForm } from './components/InputForm'
import { ProgressDisplay } from './components/ProgressDisplay'
import { ResultsDisplay } from './components/ResultsDisplay'
import { ErrorDisplay } from './components/ErrorDisplay'
import type { ResearchFormData } from './components/InputForm'

/**
 * Application state enum for clear state management
 */
type AppState = 'idle' | 'loading' | 'success' | 'error'

/**
 * Research request data for SSE connection
 */
interface ResearchRequestData {
  topic: string
  numSources: number
  outputFormat: 'json' | 'markdown'
}

/**
 * Research AI Assistant - Main Application Component
 * 
 * This component manages the overall application state and renders
 * the input form, progress display, and results display components.
 * 
 * State Flow: idle → loading → success/error
 * - InputForm: Always visible, disabled during loading
 * - ProgressDisplay: Visible during loading state
 * - ResultsDisplay: Visible on success state
 * - ErrorDisplay: Visible on error state with retry option
 * 
 * Requirements: All frontend requirements (1.1, 1.4, 2.1, 2.3, 3.1, 3.4, 8.1-8.8, 9.1-9.4, 10.1-10.6, 11.3-11.5)
 */
function App() {
  // Application state management
  const [appState, setAppState] = useState<AppState>('idle')
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [outputFormat, setOutputFormat] = useState<'json' | 'markdown'>('markdown')
  const [requestData, setRequestData] = useState<ResearchRequestData | null>(null)
  const [lastFormData, setLastFormData] = useState<ResearchFormData | null>(null)
  const [copySuccess, setCopySuccess] = useState(false)

  // Derived state for cleaner conditionals
  const isLoading = appState === 'loading'
  const hasError = appState === 'error'
  const hasResult = appState === 'success' && result !== null

  /**
   * Handle form submission - starts research workflow
   * Requirements: 1.1, 2.1, 3.1
   */
  const handleSubmit = useCallback((data: ResearchFormData) => {
    setAppState('loading')
    setError(null)
    setResult(null)
    setOutputFormat(data.outputFormat)
    setLastFormData(data) // Store for retry functionality
    setRequestData({
      topic: data.topic,
      numSources: data.numSources,
      outputFormat: data.outputFormat,
    })
  }, [])

  /**
   * Handle successful research completion
   * Requirements: 9.1-9.4
   */
  const handleComplete = useCallback((resultData: string, format: 'json' | 'markdown') => {
    setResult(resultData)
    setOutputFormat(format)
    setAppState('success')
    setRequestData(null)
  }, [])

  /**
   * Handle research error
   * Requirements: 11.3, 11.4, 11.5
   */
  const handleError = useCallback((message: string) => {
    setError(message)
    setAppState('error')
    setRequestData(null)
  }, [])

  /**
   * Handle user cancellation
   */
  const handleCancel = useCallback(() => {
    setAppState('idle')
    setRequestData(null)
  }, [])

  /**
   * Handle retry after error - resubmits last form data
   * Requirements: 11.3, 11.4
   */
  const handleRetry = useCallback(() => {
    if (lastFormData) {
      handleSubmit(lastFormData)
    }
  }, [lastFormData, handleSubmit])

  /**
   * Dismiss error and return to idle state
   */
  const handleDismissError = useCallback(() => {
    setError(null)
    setAppState('idle')
  }, [])

  /**
   * Start new research - clears results and returns to idle
   */
  const handleNewResearch = useCallback(() => {
    setResult(null)
    setError(null)
    setAppState('idle')
    setLastFormData(null)
  }, [])

  /**
   * Copy result to clipboard
   * Requirements: 10.1, 10.2
   */
  const handleCopy = useCallback(async () => {
    if (!result) return
    
    try {
      await navigator.clipboard.writeText(result)
      setCopySuccess(true)
      // Reset success state after 2 seconds
      setTimeout(() => setCopySuccess(false), 2000)
    } catch (err) {
      console.error('Failed to copy to clipboard:', err)
    }
  }, [result])

  /**
   * Download result as file
   * Requirements: 10.3, 10.4, 10.5, 10.6
   */
  const handleDownload = useCallback(() => {
    if (!result) return

    // Determine file extension based on format
    const extension = outputFormat === 'markdown' ? 'md' : 'json'
    const mimeType = outputFormat === 'markdown' ? 'text/markdown' : 'application/json'
    const filename = `research-results.${extension}`

    // Create blob and download
    const blob = new Blob([result], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }, [result, outputFormat])

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <header className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-2">
            <span className="text-4xl" role="img" aria-label="Research">🔬</span>
            <h1 className="text-3xl font-bold text-gray-900">
              Research AI Assistant
            </h1>
          </div>
          <p className="text-gray-600 mt-2">
            Enter a topic to get a comprehensive research summary with citations
          </p>
          <p className="text-sm text-gray-500 mt-1">
            Supports English and Persian • Powered by GPT-4o
          </p>
        </header>

        <main className="space-y-6">
          {/* InputForm component - Always visible */}
          <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 transition-all hover:shadow-md">
            <InputForm onSubmit={handleSubmit} isLoading={isLoading} />
          </section>

          {/* ProgressDisplay component - Requirements 8.1-8.8 */}
          {isLoading && requestData && (
            <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-fade-in">
              <ProgressDisplay
                topic={requestData.topic}
                numSources={requestData.numSources}
                outputFormat={requestData.outputFormat}
                onComplete={handleComplete}
                onError={handleError}
                onCancel={handleCancel}
              />
            </section>
          )}

          {/* Error display with retry - Requirements 11.3, 11.4, 11.5 */}
          {hasError && error && (
            <ErrorDisplay
              message={error}
              onRetry={lastFormData ? handleRetry : undefined}
              onDismiss={handleDismissError}
              canRetry={!!lastFormData}
            />
          )}

          {/* ResultsDisplay component - Requirements 9.1, 9.2, 9.3, 9.4, 10.1-10.6 */}
          {hasResult && result && (
            <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-fade-in">
              {/* New Research button */}
              <div className="flex justify-end mb-4">
                <button
                  onClick={handleNewResearch}
                  className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  New Research
                </button>
              </div>
              <ResultsDisplay
                result={result}
                format={outputFormat}
                onCopy={handleCopy}
                onDownload={handleDownload}
                copySuccess={copySuccess}
              />
            </section>
          )}

          {/* Empty state - shown when idle with no results */}
          {appState === 'idle' && !result && (
            <section className="text-center py-12 text-gray-500">
              <div className="text-6xl mb-4" role="img" aria-label="Search">🔍</div>
              <p className="text-lg">Enter a topic above to start your research</p>
              <p className="text-sm mt-2">
                The AI will search the web, analyze sources, and create a comprehensive report
              </p>
            </section>
          )}
        </main>

        {/* Footer */}
        <footer className="text-center mt-12 text-sm text-gray-500">
          <p>Research AI Assistant • Powered by DuckDuckGo Search & OpenAI GPT-4o</p>
        </footer>
      </div>
    </div>
  )
}

export default App
