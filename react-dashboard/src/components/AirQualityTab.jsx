import React from 'react'
import { Wind, AlertCircle, Gauge, Activity } from 'lucide-react'

export default function AirQualityTab() {
  const aqiValue = 42
  const aqiStatus = "Good (Safe Ambient Conditions)"
  const aqiColor = "#3fb950"

  const pollutants = [
    { name: "PM 2.5", val: "18.3", unit: "µg/m³", max: "60", label: "Fine Particulate Matter", status: "Good" },
    { name: "PM 10", val: "34.1", unit: "µg/m³", max: "100", label: "Coarse Particulate Matter", status: "Good" },
    { name: "CO2", val: "412.0", unit: "PPM", max: "1000", label: "Carbon Dioxide", status: "Normal" },
    { name: "CO", val: "0.64", unit: "mg/m³", max: "4.0", label: "Carbon Monoxide", status: "Safe" },
    { name: "CH4", val: "1.82", unit: "PPM", max: "5.0", label: "Methane Trace", status: "Normal" },
    { name: "NH3", val: "0.08", unit: "PPM", max: "25.0", label: "Ammonia Concentration", status: "Safe" }
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* SVG AQI Gauge Card */}
        <div className="rounded-lg bg-[#161b22] border border-[#30363d] p-5 shadow-sm flex flex-col items-center justify-center">
          <div className="w-full flex items-center justify-between text-xs text-[#8b949e] mb-2">
            <span className="font-semibold uppercase tracking-wider">Air Quality Index</span>
            <Gauge className="h-4 w-4 text-[#38bdf8]" />
          </div>

          <div className="relative w-48 h-32 flex items-center justify-center">
            <svg className="w-full h-full" viewBox="0 0 200 120">
              {/* Arc background */}
              <path
                d="M 20 100 A 80 80 0 0 1 180 100"
                fill="none"
                stroke="#21262d"
                strokeWidth="16"
                strokeLinecap="round"
              />
              {/* Arc colored indicator */}
              <path
                d="M 20 100 A 80 80 0 0 1 180 100"
                fill="none"
                stroke="#3fb950"
                strokeWidth="16"
                strokeDasharray="251"
                strokeDashoffset="180"
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute top-14 text-center">
              <div className="text-3xl font-bold font-mono text-white">{aqiValue}</div>
              <div className="text-[10px] uppercase font-semibold text-[#3fb950]">AQI</div>
            </div>
          </div>

          <div className="text-center mt-2">
            <span className="px-2.5 py-1 rounded-full bg-[#238636]/20 text-[#3fb950] border border-[#238636]/40 text-xs font-semibold">
              {aqiStatus}
            </span>
            <div className="text-[11px] text-[#8b949e] mt-2">
              Sensor: <code className="text-[#58a6ff]">Sensor_Air_quality_aqi</code>
            </div>
          </div>
        </div>

        {/* Gas and Particulates Grid */}
        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {pollutants.map((p, idx) => (
            <div key={idx} className="rounded-lg bg-[#161b22] border border-[#30363d] p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white tracking-wide">{p.name}</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#238636]/20 text-[#3fb950] border border-[#238636]/40 font-mono">
                  {p.status}
                </span>
              </div>
              <div className="text-[11px] text-[#8b949e] mt-0.5">{p.label}</div>

              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-xl font-bold text-white font-mono">{p.val}</span>
                <span className="text-xs text-[#8b949e] font-mono">{p.unit}</span>
              </div>

              {/* Progress bar */}
              <div className="mt-2 w-full bg-[#0d1117] h-1.5 rounded-full overflow-hidden border border-[#21262d]">
                <div
                  className="bg-[#38bdf8] h-full rounded-full"
                  style={{ width: `${Math.min(100, (parseFloat(p.val) / parseFloat(p.max)) * 100)}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-[10px] text-[#8b949e] mt-1 font-mono">
                <span>Threshold: {p.max} {p.unit}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

