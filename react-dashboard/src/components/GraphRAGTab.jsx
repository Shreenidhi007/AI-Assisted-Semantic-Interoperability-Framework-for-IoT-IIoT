import React, { useState } from 'react'
import { MessageSquare, Sparkles, Code, Play, Terminal, CheckCircle2 } from 'lucide-react'
import { queryGraphRag } from '../api'

export default function GraphRAGTab() {
  const [question, setQuestion] = useState('What are the latest observations recorded across domains?')
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState(null)
  const [showSparql, setShowSparql] = useState(true)

  const presets = [
    "What are the latest observations recorded across domains?",
    "List all deployed W3C SOSA Sensors and host Platforms",
    "What is the highest temperature recorded in hydroponics?",
    "Identify offline sensors with hardware fault codes (-1.0)",
    "Compare ambient temperature between hydroponics and air quality",
    "Find all observations exceeding threshold 100"
  ]

  const handleQuery = async (qText) => {
    const q = qText || question
    if (!q) return
    setLoading(true)
    try {
      const res = await queryGraphRag(q)
      setResponse(res)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-lg bg-[#161b22] border border-[#30363d] p-5 shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="h-5 w-5 text-[#38bdf8]" />
          <h2 className="text-base font-semibold text-white">
            Natural Language to SPARQL Graph-RAG Explorer
          </h2>
        </div>
        <p className="text-xs text-[#8b949e] mb-4">
          Query the <strong className="text-[#c9d1d9]">1,045,274+ triple Knowledge Graph</strong> in plain English. The agent translates your question into standard W3C SPARQL 1.1 queries and executes them with zero hallucinations.
        </p>

        {/* Preset query chips */}
        <div className="flex flex-wrap gap-2 mb-4">
          {presets.map((p, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuestion(p)
                handleQuery(p)
              }}
              className="px-2.5 py-1 rounded-full bg-[#0d1117] hover:bg-[#21262d] border border-[#30363d] text-[11px] text-[#c9d1d9] transition-colors"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Input box */}
        <div className="flex gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
              placeholder="Ask an environmental IoT question in plain English..."
              className="w-full rounded-lg bg-[#0d1117] border border-[#30363d] px-4 py-2.5 text-xs text-[#c9d1d9] placeholder-[#8b949e] focus:border-[#38bdf8] focus:outline-none"
            />
          </div>
          <button
            onClick={() => handleQuery()}
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#238636] hover:bg-[#2ea043] text-white text-xs font-semibold shadow-md transition-colors disabled:opacity-50"
          >
            <Play className={`h-3.5 w-3.5 fill-current ${loading ? 'animate-pulse' : ''}`} />
            <span>{loading ? 'Translating...' : 'Run Query'}</span>
          </button>
        </div>
      </div>

      {/* Response Box */}
      {response && (
        <div className="rounded-lg bg-[#161b22] border border-[#30363d] p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs">
              <CheckCircle2 className="h-4 w-4 text-[#3fb950]" />
              <span className="font-semibold text-white">{response.summary}</span>
            </div>
            <button
              onClick={() => setShowSparql(!showSparql)}
              className="flex items-center gap-1.5 text-xs text-[#58a6ff] hover:underline font-mono"
            >
              <Code className="h-3.5 w-3.5" />
              <span>{showSparql ? 'Hide SPARQL' : 'View Generated SPARQL'}</span>
            </button>
          </div>

          {/* SPARQL Query Block */}
          {showSparql && response.sparql_query && (
            <div className="rounded-lg bg-[#0d1117] border border-[#30363d] p-3 text-xs font-mono text-[#79c0ff] overflow-x-auto">
              <pre>{response.sparql_query}</pre>
            </div>
          )}

          {/* Results Table */}
          {response.results && response.results.length > 0 ? (
            <div className="overflow-x-auto rounded-lg border border-[#30363d]">
              <table className="w-full text-left text-xs text-[#c9d1d9]">
                <thead className="bg-[#0d1117] text-[#8b949e] uppercase text-[10px] tracking-wider border-b border-[#30363d]">
                  <tr>
                    {Object.keys(response.results[0]).map((key) => (
                      <th key={key} className="py-2 px-3">{key}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#21262d] font-mono">
                  {response.results.map((row, idx) => (
                    <tr key={idx} className="hover:bg-[#21262d]/50">
                      {Object.values(row).map((val, cIdx) => (
                        <td key={cIdx} className="py-2 px-3">{String(val)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-xs text-[#8b949e] py-3 text-center">
              No matching triples returned for this SPARQL query.
            </div>
          )}
        </div>
      )}
    </div>
  )
}

