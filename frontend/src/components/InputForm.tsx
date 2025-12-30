import { useState } from 'react'
import type { FormEvent } from 'react'

export interface ResearchFormData {
  topic: string
  numSources: number
  outputFormat: 'json' | 'markdown'
}

interface InputFormProps {
  onSubmit: (data: ResearchFormData) => void
  isLoading?: boolean
}

/**
 * InputForm Component
 * 
 * Provides a form for users to enter research parameters:
 * - Research topic (supports English and Persian)
 * - Number of sources (3-10, default 5)
 * - Output format (JSON/Markdown, default Markdown)
 * 
 * Requirements: 1.1, 2.1, 2.3, 3.1, 3.4, 1.4
 */
export function InputForm({ onSubmit, isLoading = false }: InputFormProps) {
  const [topic, setTopic] = useState('')
  const [numSources, setNumSources] = useState(5)
  const [outputFormat, setOutputFormat] = useState<'json' | 'markdown'>('markdown')
  const [validationError, setValidationError] = useState<string | null>(null)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    
    // Validate topic - reject empty or whitespace-only input (Requirement 1.4)
    const trimmedTopic = topic.trim()
    if (!trimmedTopic) {
      setValidationError('Please enter a research topic')
      return
    }
    
    // Clear any previous validation error
    setValidationError(null)
    
    // Submit the form data
    onSubmit({
      topic: trimmedTopic,
      numSources,
      outputFormat
    })
  }

  // Generate source count options (3-10) - Requirement 2.1
  const sourceOptions = Array.from({ length: 8 }, (_, i) => i + 3)

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Research Topic Input - Requirement 1.1 */}
      <div>
        <label 
          htmlFor="topic" 
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Research Topic
        </label>
        <input
          type="text"
          id="topic"
          value={topic}
          onChange={(e) => {
            setTopic(e.target.value)
            if (validationError) setValidationError(null)
          }}
          placeholder="Enter your research topic (English or Persian)"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
          dir="auto"
          disabled={isLoading}
        />
        {validationError && (
          <p className="mt-2 text-sm text-red-600" role="alert">
            {validationError}
          </p>
        )}
      </div>

      {/* Source Count Dropdown - Requirements 2.1, 2.3 */}
      <div>
        <label 
          htmlFor="numSources" 
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Number of Sources
        </label>
        <select
          id="numSources"
          value={numSources}
          onChange={(e) => setNumSources(Number(e.target.value))}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors bg-white"
          disabled={isLoading}
        >
          {sourceOptions.map((num) => (
            <option key={num} value={num}>
              {num} sources
            </option>
          ))}
        </select>
        <p className="mt-1 text-sm text-gray-500">
          Choose between 3 and 10 sources (default: 5)
        </p>
      </div>

      {/* Output Format Radio Buttons - Requirements 3.1, 3.4 */}
      <div>
        <fieldset>
          <legend className="block text-sm font-medium text-gray-700 mb-2">
            Output Format
          </legend>
          <div className="flex gap-6">
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="outputFormat"
                value="markdown"
                checked={outputFormat === 'markdown'}
                onChange={() => setOutputFormat('markdown')}
                className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                disabled={isLoading}
              />
              <span className="ml-2 text-gray-700">Markdown</span>
            </label>
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="outputFormat"
                value="json"
                checked={outputFormat === 'json'}
                onChange={() => setOutputFormat('json')}
                className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                disabled={isLoading}
              />
              <span className="ml-2 text-gray-700">JSON</span>
            </label>
          </div>
          <p className="mt-1 text-sm text-gray-500">
            Default: Markdown
          </p>
        </fieldset>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 disabled:bg-blue-400 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg 
              className="animate-spin h-5 w-5" 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24"
            >
              <circle 
                className="opacity-25" 
                cx="12" 
                cy="12" 
                r="10" 
                stroke="currentColor" 
                strokeWidth="4"
              />
              <path 
                className="opacity-75" 
                fill="currentColor" 
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Researching...
          </span>
        ) : (
          'Start Research'
        )}
      </button>
    </form>
  )
}
