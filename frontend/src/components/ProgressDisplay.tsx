import { useEffect, useState, useRef } from 'react'

/**
 * Progress step definition
 */
interface ProgressStep {
  id: string
  label: string
  status: 'pending' | 'active' | 'completed'
  message?: string
  current?: number
  total?: number
  count?: number
}

/**
 * SSE Progress event from backend
 */
interface ProgressEvent {
  step: string
  message: string
  current?: number
  total?: number
  count?: number
}

/**
 * SSE Complete event from backend
 */
interface CompleteEvent {
  result: string
  format: 'json' | 'markdown'
}

/**
 * SSE Error event from backend
 */
interface ErrorEvent {
  message: string
}

interface ProgressDisplayProps {
  topic: string
  numSources: number
  outputFormat: 'json' | 'markdown'
  onComplete: (result: string, format: 'json' | 'markdown') => void
  onError: (message: string) => void
  onCancel: () => void
}

/**
 * Default progress steps matching backend SSE events
 * Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8
 */
const DEFAULT_STEPS: ProgressStep[] = [
  { id: 'searching', label: 'Searching', status: 'pending' },
  { id: 'found', label: 'Sources Found', status: 'pending' },
  { id: 'fetching', label: 'Fetching Pages', status: 'pending' },
  { id: 'summarizing', label: 'Summarizing', status: 'pending' },
  { id: 'analyzing', label: 'Analyzing', status: 'pending' },
  { id: 'finalizing', label: 'Finalizing', status: 'pending' },
]

/**
 * ProgressDisplay Component
 * 
 * Connects to SSE stream and displays real-time progress updates
 * with step-by-step visualization and icons.
 * 
 * Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8
 */
export function ProgressDisplay({
  topic,
  numSources,
  outputFormat,
  onComplete,
  onError,
  onCancel,
}: ProgressDisplayProps) {
  const [steps, setSteps] = useState<ProgressStep[]>(DEFAULT_STEPS)
  const [currentMessage, setCurrentMessage] = useState<string>('Starting research...')
  const eventSourceRef = useRef<EventSource | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  useEffect(() => {
    // Start SSE connection
    connectToSSE()

    // Cleanup on unmount
    return () => {
      closeConnection()
    }
  }, [])

  const connectToSSE = async () => {
    try {
      // Create abort controller for fetch
      abortControllerRef.current = new AbortController()

      // Make POST request to initiate research
      const response = await fetch('http://localhost:8000/api/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          num_sources: numSources,
          output_format: outputFormat,
        }),
        signal: abortControllerRef.current.signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Read SSE stream
      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) {
          break
        }

        buffer += decoder.decode(value, { stream: true })
        
        // Process complete SSE events
        const events = buffer.split('\n\n')
        buffer = events.pop() || '' // Keep incomplete event in buffer

        for (const eventStr of events) {
          if (eventStr.trim()) {
            processSSEEvent(eventStr)
          }
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        // Request was cancelled, don't report as error
        return
      }
      onError(error instanceof Error ? error.message : 'Connection failed')
    }
  }

  const processSSEEvent = (eventStr: string) => {
    const lines = eventStr.split('\n')
    let eventType = ''
    let eventData = ''

    for (const line of lines) {
      if (line.startsWith('event: ')) {
        eventType = line.slice(7).trim()
      } else if (line.startsWith('data: ')) {
        eventData = line.slice(6).trim()
      }
    }

    if (!eventType || !eventData) return

    try {
      const data = JSON.parse(eventData)

      switch (eventType) {
        case 'progress':
          handleProgressEvent(data as ProgressEvent)
          break
        case 'complete':
          handleCompleteEvent(data as CompleteEvent)
          break
        case 'error':
          handleErrorEvent(data as ErrorEvent)
          break
      }
    } catch (e) {
      console.error('Failed to parse SSE event:', e)
    }
  }

  const handleProgressEvent = (event: ProgressEvent) => {
    setCurrentMessage(event.message)

    setSteps(prevSteps => {
      const newSteps = [...prevSteps]
      const stepIndex = newSteps.findIndex(s => s.id === event.step)

      if (stepIndex !== -1) {
        // Mark all previous steps as completed
        for (let i = 0; i < stepIndex; i++) {
          newSteps[i] = { ...newSteps[i], status: 'completed' }
        }

        // Update current step
        newSteps[stepIndex] = {
          ...newSteps[stepIndex],
          status: 'active',
          message: event.message,
          current: event.current,
          total: event.total,
          count: event.count,
        }
      }

      return newSteps
    })
  }

  const handleCompleteEvent = (event: CompleteEvent) => {
    // Mark all steps as completed
    setSteps(prevSteps => 
      prevSteps.map(step => ({ ...step, status: 'completed' as const }))
    )
    setCurrentMessage('Research complete!')
    onComplete(event.result, event.format)
  }

  const handleErrorEvent = (event: ErrorEvent) => {
    onError(event.message)
  }

  const closeConnection = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
  }

  const handleCancel = () => {
    closeConnection()
    onCancel()
  }

  /**
   * Get icon for step based on status
   */
  const getStepIcon = (step: ProgressStep) => {
    switch (step.status) {
      case 'completed':
        return (
          <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        )
      case 'active':
        return (
          <svg className="w-5 h-5 text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        )
      default:
        return (
          <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
        )
    }
  }

  /**
   * Get step-specific icon based on step id
   */
  const getStepTypeIcon = (stepId: string) => {
    switch (stepId) {
      case 'searching':
        return '🔍'
      case 'found':
        return '📚'
      case 'fetching':
        return '📄'
      case 'summarizing':
        return '🤖'
      case 'analyzing':
        return '🧠'
      case 'finalizing':
        return '✍️'
      default:
        return '📋'
    }
  }

  return (
    <div className="space-y-4">
      {/* Current status message */}
      <div className="text-center">
        <p className="text-lg font-medium text-gray-700">{currentMessage}</p>
      </div>

      {/* Progress steps */}
      <div className="space-y-3">
        {steps.map((step, index) => (
          <div
            key={step.id}
            className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
              step.status === 'active'
                ? 'bg-blue-50 border border-blue-200'
                : step.status === 'completed'
                ? 'bg-green-50 border border-green-200'
                : 'bg-gray-50 border border-gray-200'
            }`}
          >
            {/* Status icon */}
            <div className="flex-shrink-0">
              {getStepIcon(step)}
            </div>

            {/* Step type icon */}
            <span className="text-xl flex-shrink-0" role="img" aria-label={step.label}>
              {getStepTypeIcon(step.id)}
            </span>

            {/* Step label and details */}
            <div className="flex-grow">
              <p className={`font-medium ${
                step.status === 'active'
                  ? 'text-blue-700'
                  : step.status === 'completed'
                  ? 'text-green-700'
                  : 'text-gray-500'
              }`}>
                {step.label}
              </p>
              
              {/* Show progress details for active step */}
              {step.status === 'active' && step.message && (
                <p className="text-sm text-gray-600 mt-1">
                  {step.message}
                </p>
              )}

              {/* Show count for 'found' step */}
              {step.id === 'found' && step.count !== undefined && step.status !== 'pending' && (
                <p className="text-sm text-gray-600 mt-1">
                  {step.count} sources found
                </p>
              )}

              {/* Show progress for fetching/summarizing steps */}
              {(step.id === 'fetching' || step.id === 'summarizing') && 
               step.current !== undefined && step.total !== undefined && 
               step.status !== 'pending' && (
                <div className="mt-2">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>{step.current} of {step.total}</span>
                    <span>{Math.round((step.current / step.total) * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(step.current / step.total) * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Step number */}
            <div className="flex-shrink-0 text-sm text-gray-400">
              {index + 1}/{steps.length}
            </div>
          </div>
        ))}
      </div>

      {/* Cancel button */}
      <div className="text-center pt-2">
        <button
          onClick={handleCancel}
          className="text-gray-500 hover:text-gray-700 text-sm underline"
        >
          Cancel research
        </button>
      </div>
    </div>
  )
}
