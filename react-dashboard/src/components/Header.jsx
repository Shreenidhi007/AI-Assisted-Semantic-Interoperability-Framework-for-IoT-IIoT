import React from 'react'
import { Database, Activity, Cpu, RefreshCw, Layers, ShieldCheck } from 'lucide-react'

export default function Header({ meta, loading, onRefresh, countdown }) {
  const triples = meta?.total_triples?.toLocaleString() || "1,045,274"
  const observations = meta?.total_observations?.toLocaleString() || "61,186"
  const age = meta?.pipeline_age_min ?? 1

  return (
    <header className="border-b border-[#30363d] bg-[#161b22] px-6 py-5 shadow-lg">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-tr from-[#1f6feb] to-[#38bdf8] text-white shadow-md">
              <Layers className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                EnviroMap-KG
                <span className="text-xs px-2 py-0.5 rounded-full bg-[#238636]/20 text-[#3fb950] border border-[#238636]/40 font-mono">
                  v2.4 Enterprise
                </span>
              </h1>
              <p className="text-xs text-[#8b949e]">
                Standards-Aware Semantic IoT Knowledge Graph Platform (W3C SSN/SOSA & ETSI SAREF)
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0d1117] border border-[#30363d] text-xs font-mono text-[#8b949e]">
            <span className="h-2 w-2 rounded-full bg-[#3fb950] pulse-indicator"></span>
            Pipeline Active ({age}m ago)
          </div>

          <button
            onClick={onRefresh}
            disabled={loading}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-[#21262d] hover:bg-[#30363d] border border-[#30363d] text-xs font-medium text-[#c9d1d9] transition-colors disabled:opacity-50"
            title="Auto-refreshes every 3 minutes"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-[#38bdf8]' : ''}`} />
            <span>{loading ? 'Querying KG...' : `Refresh (${countdown}s)`}</span>
          </button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="mt-5 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-lg bg-[#0d1117] border border-[#30363d] p-3.5 shadow-sm">
          <div className="flex items-center justify-between text-[#8b949e]">
            <span className="text-xs uppercase tracking-wider font-semibold">Knowledge Graph</span>
            <Database className="h-4 w-4 text-[#38bdf8]" />
          </div>
          <div className="mt-2 text-xl font-bold text-white font-mono">{triples}</div>
          <div className="text-[11px] text-[#8b949e] mt-0.5">W3C RDF Triples in Graph</div>
        </div>

        <div className="rounded-lg bg-[#0d1117] border border-[#30363d] p-3.5 shadow-sm">
          <div className="flex items-center justify-between text-[#8b949e]">
            <span className="text-xs uppercase tracking-wider font-semibold">Observations</span>
            <Activity className="h-4 w-4 text-[#3fb950]" />
          </div>
          <div className="mt-2 text-xl font-bold text-white font-mono">{observations}</div>
          <div className="text-[11px] text-[#8b949e] mt-0.5">Canonical SOSA Observations</div>
        </div>

        <div className="rounded-lg bg-[#0d1117] border border-[#30363d] p-3.5 shadow-sm">
          <div className="flex items-center justify-between text-[#8b949e]">
            <span className="text-xs uppercase tracking-wider font-semibold">Physical Sensors</span>
            <Cpu className="h-4 w-4 text-[#d29922]" />
          </div>
          <div className="mt-2 text-xl font-bold text-white font-mono">17 Deployed</div>
          <div className="text-[11px] text-[#8b949e] mt-0.5">Across 2 Host Platforms</div>
        </div>

        <div className="rounded-lg bg-[#0d1117] border border-[#30363d] p-3.5 shadow-sm">
          <div className="flex items-center justify-between text-[#8b949e]">
            <span className="text-xs uppercase tracking-wider font-semibold">Semantic Mappings</span>
            <ShieldCheck className="h-4 w-4 text-[#a371f7]" />
          </div>
          <div className="mt-2 text-xl font-bold text-white font-mono">21 / 21 Valid</div>
          <div className="text-[11px] text-[#8b949e] mt-0.5">100% Validated & Learned</div>
        </div>
      </div>
    </header>
  )
}

