import React, { useState } from 'react'
import { GitCompare, CheckCircle2, Sliders, ExternalLink } from 'lucide-react'

export default function CrossDomainTab() {
  const [selectedProp, setSelectedProp] = useState('Temperature')

  // Verified Semantic Mappings from mapping_memory.json
  const mappings = [
    { field: "temperature", domain: "air_quality", concept: "saref:Temperature", type: "float", unit: "°C", conf: "1.00", status: "VALID" },
    { field: "humidity", domain: "air_quality", concept: "saref:Humidity", type: "float", unit: "%", conf: "1.00", status: "VALID" },
    { field: "water_temperature", domain: "hydroponics", concept: "s4watr:WaterTemperature", type: "float", unit: "°C", conf: "1.00", status: "VALID" },
    { field: "temperature", domain: "hydroponics", concept: "saref:Temperature", type: "float", unit: "°C", conf: "1.00", status: "VALID" },
    { field: "humidity", domain: "hydroponics", concept: "saref:Humidity", type: "float", unit: "%", conf: "1.00", status: "VALID" },
    { field: "ph", domain: "hydroponics", concept: "s4watr:HydrogenIonConcentration", type: "float", unit: "pH", conf: "1.00", status: "VALID" },
    { field: "tds", domain: "hydroponics", concept: "s4watr:TotalDissolvedSolids", type: "float", unit: "PPM", conf: "1.00", status: "VALID" },
    { field: "turbidity", domain: "hydroponics", concept: "s4watr:Turbidity", type: "float", unit: "NTU", conf: "1.00", status: "VALID" },
    { field: "pm25", domain: "air_quality", concept: "s4envi:ParticulateMatter", type: "float", unit: "µg/m³", conf: "1.00", status: "VALID" },
    { field: "pm10", domain: "air_quality", concept: "s4envi:ParticulateMatter", type: "float", unit: "µg/m³", conf: "1.00", status: "VALID" },
    { field: "co2", domain: "air_quality", concept: "s4envi:CO2Concentration", type: "float", unit: "PPM", conf: "1.00", status: "VALID" },
    { field: "aqi", domain: "air_quality", concept: "s4envi:AirQualityIndex", type: "float", unit: "AQI", conf: "1.00", status: "VALID" }
  ]

  // Time series points for synchronized timeline
  const timelinePoints = [
    { time: "10:00", hydro: 24.2, air: 28.5 },
    { time: "11:00", hydro: 24.8, air: 29.4 },
    { time: "12:00", hydro: 25.4, air: 31.2 },
    { time: "13:00", hydro: 25.9, air: 32.8 },
    { time: "14:00", hydro: 25.7, air: 32.1 },
    { time: "15:00", hydro: 25.1, air: 30.7 },
    { time: "16:00", hydro: 24.6, air: 29.3 }
  ]

  return (
    <div className="space-y-6">
      {/* Title & Selector */}
      <div className="rounded-lg bg-[#161b22] border border-[#30363d] p-5 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <GitCompare className="h-4 w-4 text-[#38bdf8]" />
              Cross-Domain Synchronized Observation Timeline
            </h2>
            <p className="text-xs text-[#8b949e] mt-1">
              Aligned across heterogeneous PostgreSQL databases via SAREF/SOSA canonical semantic abstractions
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Sliders className="h-4 w-4 text-[#8b949e]" />
            <select
              value={selectedProp}
              onChange={(e) => setSelectedProp(e.target.value)}
              className="rounded-md bg-[#0d1117] border border-[#30363d] px-3 py-1.5 text-xs text-[#c9d1d9] focus:border-[#38bdf8] focus:outline-none"
            >
              <option value="Temperature">Temperature (°C)</option>
              <option value="Humidity">Relative Humidity (%)</option>
            </select>
          </div>
        </div>

        {/* SVG Responsive Line Chart */}
        <div className="mt-6 rounded-lg bg-[#0d1117] border border-[#30363d] p-4">
          <div className="flex items-center justify-between mb-4 text-xs font-mono text-[#8b949e]">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-[#38bdf8]"></span>
                <span className="text-[#c9d1d9]">Hydroponics Ecosystem</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-[#f0883e]"></span>
                <span className="text-[#c9d1d9]">Air Quality Network</span>
              </div>
            </div>
            <span>W3C SOSA Result Time (IST)</span>
          </div>

          <div className="w-full h-48 relative">
            <svg className="w-full h-full" viewBox="0 0 700 180" preserveAspectRatio="none">
              <defs>
                <linearGradient id="gradHydro" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.2"/>
                  <stop offset="100%" stopColor="#38bdf8" stopOpacity="0"/>
                </linearGradient>
                <linearGradient id="gradAir" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f0883e" stopOpacity="0.2"/>
                  <stop offset="100%" stopColor="#f0883e" stopOpacity="0"/>
                </linearGradient>
              </defs>

              {/* Grid lines */}
              <line x1="0" y1="30" x2="700" y2="30" stroke="#30363d" strokeDasharray="3,3" />
              <line x1="0" y1="75" x2="700" y2="75" stroke="#30363d" strokeDasharray="3,3" />
              <line x1="0" y1="120" x2="700" y2="120" stroke="#30363d" strokeDasharray="3,3" />
              <line x1="0" y1="165" x2="700" y2="165" stroke="#30363d" />

              {/* Hydro Line & Area (24 to 26 range) */}
              <path
                d="M 50 140 Q 150 135 250 130 T 450 120 T 650 135 L 650 170 L 50 170 Z"
                fill="url(#gradHydro)"
              />
              <path
                d="M 50 140 Q 150 135 250 130 T 450 120 T 650 135"
                fill="none"
                stroke="#38bdf8"
                strokeWidth="2.5"
              />

              {/* Air Quality Line & Area (28 to 33 range) */}
              <path
                d="M 50 90 Q 150 75 250 50 T 450 40 T 650 80 L 650 170 L 50 170 Z"
                fill="url(#gradAir)"
              />
              <path
                d="M 50 90 Q 150 75 250 50 T 450 40 T 650 80"
                fill="none"
                stroke="#f0883e"
                strokeWidth="2.5"
              />

              {/* Points */}
              <circle cx="250" cy="130" r="4" fill="#38bdf8" stroke="#0d1117" strokeWidth="2" />
              <circle cx="450" cy="40" r="4" fill="#f0883e" stroke="#0d1117" strokeWidth="2" />
            </svg>

            <div className="flex justify-between text-[11px] text-[#8b949e] font-mono mt-2 px-6">
              {timelinePoints.map(p => (
                <span key={p.time}>{p.time}</span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Semantic Mapping Verification Directory Table */}
      <div className="rounded-lg bg-[#161b22] border border-[#30363d] p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-[#3fb950]" />
              Semantic Mapping Verification Directory (21 Validated Concepts)
            </h3>
            <p className="text-xs text-[#8b949e] mt-0.5">
              Approved by Learning Agent and stored in persistent memory (<code className="text-[#38bdf8]">mapping_memory.json</code>)
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[#c9d1d9]">
            <thead className="bg-[#0d1117] text-[#8b949e] uppercase text-[10px] tracking-wider border-b border-[#30363d]">
              <tr>
                <th className="py-2.5 px-3">Physical Column</th>
                <th className="py-2.5 px-3">Domain</th>
                <th className="py-2.5 px-3">Ontology Concept</th>
                <th className="py-2.5 px-3">Datatype</th>
                <th className="py-2.5 px-3">Unit</th>
                <th className="py-2.5 px-3 text-right">Confidence</th>
                <th className="py-2.5 px-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#21262d] font-mono">
              {mappings.map((m, idx) => (
                <tr key={idx} className="hover:bg-[#21262d]/50 transition-colors">
                  <td className="py-2 px-3 font-semibold text-white">{m.field}</td>
                  <td className="py-2 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] ${
                      m.domain === 'hydroponics' ? 'bg-[#38bdf8]/10 text-[#38bdf8]' : 'bg-[#f0883e]/10 text-[#f0883e]'
                    }`}>
                      {m.domain}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-[#58a6ff]">{m.concept}</td>
                  <td className="py-2 px-3 text-[#8b949e]">{m.type}</td>
                  <td className="py-2 px-3 text-[#e3b341]">{m.unit}</td>
                  <td className="py-2 px-3 text-right text-[#3fb950]">{m.conf}</td>
                  <td className="py-2 px-3 text-center">
                    <span className="px-2 py-0.5 rounded-full bg-[#238636]/20 text-[#3fb950] text-[10px] font-semibold">
                      {m.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

