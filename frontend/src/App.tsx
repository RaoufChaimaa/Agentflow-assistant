import { useState } from 'react'
import './App.css'

type Mode = 'summary' | 'qa' | 'tasks'

interface ApiResponse {
  result: string
  mode: string
  latency_ms: number
}

export default function App() {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState<ApiResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeMode, setActiveMode] = useState<Mode | null>(null)

  const getPageText = async (): Promise<string> => {
    if (typeof chrome !== 'undefined' && chrome.tabs) {
      return new Promise((resolve) => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          if (!tabs[0]?.id) return resolve('')
          chrome.scripting.executeScript(
            { target: { tabId: tabs[0].id! }, func: () => document.body.innerText },
            (results) => resolve(results?.[0]?.result ?? '')
          )
        })
      })
    }

    return 'This is a demo page about quarterly earnings. Action items: review budget by Friday, schedule team sync, update project roadmap. Deadline is end of Q2.'
  }

  const callApi = async (mode: Mode, userQuestion?: string) => {
    setLoading(true)
    setError('')
    setResult(null)
    setActiveMode(mode)

    try {
      const pageText = await getPageText()
      const res = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          page_text: pageText,
          mode,
          question: userQuestion || '',
        }),
      })

      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data: ApiResponse = await res.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const handleQuestion = () => {
    if (!question.trim()) {
      setError('Please enter a question.')
      return
    }
    callApi('qa', question)
  }

  return (
    <div className="popup">
      <header className="header">
        <span className="logo">⬡</span>
        <span className="brand">AgentFlow</span>
        <span className="tag">AI Assistant</span>
      </header>

      <div className="section">
        <label className="label">Ask a question about this page</label>
        <textarea
          className="textarea"
          placeholder="e.g. What is the main deadline mentioned?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleQuestion()
            }
          }}
          rows={3}
        />
        <button
          className="btn btn-primary"
          onClick={handleQuestion}
          disabled={loading}
        >
          {loading && activeMode === 'qa' ? <span className="spinner" /> : '→'}
          Ask Question
        </button>
      </div>

      <div className="divider">
        <span>or use quick actions</span>
      </div>

      <div className="actions">
        <button
          className="btn btn-action"
          onClick={() => callApi('summary')}
          disabled={loading}
        >
          {loading && activeMode === 'summary' ? <span className="spinner" /> : '◈'}
          Summarize Page
        </button>
        <button
          className="btn btn-action"
          onClick={() => callApi('tasks')}
          disabled={loading}
        >
          {loading && activeMode === 'tasks' ? <span className="spinner" /> : '◎'}
          Extract Tasks
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="result">
          <div className="result-header">
            <span className="result-mode">{result.mode.toUpperCase()}</span>
            <span className="result-latency">{result.latency_ms}ms</span>
          </div>
          <p className="result-text">{result.result}</p>
        </div>
      )}

      <footer className="footer">
        Powered by LangGraph · FastAPI
      </footer>
    </div>
  )
}