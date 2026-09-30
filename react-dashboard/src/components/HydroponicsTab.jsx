import React from 'react'
import { Droplets, Thermometer, Wind, Activity, AlertTriangle, ShieldCheck } from 'lucide-react'

export default function HydroponicsTab() {
  const metrics = [
    { title: "Water Temperature", val: "22.4", unit: "°C", concept: "s4watr:WaterTemperature", optimal: "18-24°C", icon: Thermometer, color: "#38bdf8" },
    { title: "Ambient Temperature", val: "24.8", unit: "°C", concept: "saref:Temperature", optimal: "20-28°C", icon: Thermometer, color: "#58a6ff" },
    { title: "Relative Humidity", val: "78.1", unit: "%", concept: "saref:Humidity", optimal: "60-80%", icon: Wind, color: "#3fb950" },
    { title: "pH Value", val: "6.42", unit: "pH", concept: "s4watr:HydrogenIonConcentration", optimal: "5.5-6.8", icon: Droplets, color: "#a371f7" },
    { title: "Total Dissolved Solids", val: "645.2", unit: "PPM", concept: "s4watr:TotalDissolvedSolids", optimal: "500-800", icon: Activity, color: "#f0883e" },
    { title: "Turbidity", val: "8.65", unit: "NTU", concept: "s4watr:Turbidity", optimal: "< 10 NTU", icon: Droplets, color: "#e3b341" }
  ]

  return (
    <div className="space-y-6">
      {/* Sensor Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {metrics.map((m, idx) => {
          const Icon = m.icon
          return (
            <div key={idx} className="rounded-lg bg-[#161b22] border border-[#30363d] p-4 shadow-sm relative overflow-hidden">
              <div className="flex items-center justify-between text-[#8b949e]">
                <span className="text-xs font-semibold uppercase tracking-wider">{m.title}</span>
                <Icon className="h-4 w-4" style={{ color: m.color }} />
              </div>

              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-2xl font-bold text-white font-mono">{m.val}</span>
                <span className="text-xs text-[#8b949e] font-mono">{m.unit}</span>
              </div>

              <div className="mt-3 flex items-center justify-between border-t border-[#21262d] pt-2 text-[11px]">
                <span className="text-[#8b949e]">Optimal: {m.optimal}</span>
                <span className="font-mono text-[#58a6ff] text-[10px]">{m.concept}</span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Hardware Sentinel & Fault Monitor */}
      <div className="rounded-lg bg-[#161b22] border border-[#30363d] p-5">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-[#e3b341]" />
            Hardware Disconnect Sentinel & Data Quality Gate
          </h3>
          <span className="px-2.5 py-1 rounded-full bg-[#238636]/20 text-[#3fb950] border border-[#238636]/40 text-xs font-mono">
            Auto-Sanitizer Active
          </span>
        </div>

        <p className="text-xs text-[#8b949e] mb-4">
          Hardware sensors in the field occasionally return sentinel error codes like <code className="text-[#f85149]">-1.0</code> (timeout) or <code className="text-[#f85149]">-127.0</code> (DS18B20 wire disconnect). The semantic translator automatically sanitizes observations to prevent skewing environmental metrics.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="rounded-lg bg-[#0d1117] border border-[#30363d] p-3 flex items-center gap-3">
            <div className="p-2 rounded-md bg-[#238636]/10 text-[#3fb950]">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <div className="font-semibold text-white">Rule-Based Cleaning Filter</div>
              <div className="text-[11px] text-[#8b949e] mt-0.5">Value &gt; -0.5 threshold enforced on all queries</div>
            </div>
          </div>

          <div className="rounded-lg bg-[#0d1117] border border-[#30363d] p-3 flex items-center gap-3">
            <div className="p-2 rounded-md bg-[#38bdf8]/10 text-[#38bdf8]">
              <Activity className="h-5 w-5" />
            </div>
            <div>
              <div className="font-semibold text-white">11,452 Hydroponics Records Mapped</div>
              <div className="text-[11px] text-[#8b949e] mt-0.5">Triplified as <code className="text-[#38bdf8]">enviromap:NutrientSolution</code> FOI</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

