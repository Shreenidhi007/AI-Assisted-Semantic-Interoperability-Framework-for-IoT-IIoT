import React from 'react'
import { BarChart3, BookOpen, Layers, CheckCircle2 } from 'lucide-react'

export default function AnalyticsTab() {
  const classDist = [
    { label: "TotalDissolvedSolids", count: "11,452", pct: 20 },
    { label: "WaterTemperature", count: "11,452", pct: 20 },
    { label: "HydrogenIonConcentration", count: "11,452", pct: 20 },
    { label: "Turbidity", count: "11,452", pct: 20 },
    { label: "Temperature (Ambient)", count: "12,233", pct: 22 },
    { label: "ParticulateMatter (PM2.5/10)", count: "1,562", pct: 3 },
    { label: "CO2Concentration", count: "781", pct: 1.5 }
  ]

  const ontologies = [
    { name: "ETSI SAREF Core", standard: "ETSI TS 103 264", desc: "Smart Applications REFerence for IoT Devices & Measurements", uri: "https://saref.etsi.org/core/" },
    { name: "W3C SSN / SOSA", standard: "W3C Recommendation", desc: "Semantic Sensor Network & Sensor, Observation, Sample, Actuator", uri: "http://www.w3.org/ns/sosa/" },
    { name: "QUDT Units", standard: "NASA / TopQuadrant", desc: "Quantities, Units, Dimensions and Data Types Ontology", uri: "http://qudt.org/vocab/unit/" },
    { name: "W3C PROV-O", standard: "W3C Recommendation", desc: "Provenance Data Model tracking agent execution lineage", uri: "http://www.w3.org/ns/prov#" }
  ]

  return (
    <div className="space-y-6">
      {/* Distribution Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-lg bg-[#161b22] border border-[#30363d] p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-4">
            <BarChart3 className="h-4 w-4 text-[#38bdf8]" />
            Observations per Semantic Class
          </h3>

          <div className="space-y-3">
            {classDist.map((item, idx) => (
              <div key={idx} className="text-xs">
                <div className="flex justify-between text-[#c9d1d9] mb-1 font-mono">
                  <span>{item.label}</span>
                  <span className="text-[#8b949e]">{item.count}</span>
                </div>
                <div className="w-full bg-[#0d1117] h-2 rounded-full overflow-hidden border border-[#21262d]">
                  <div
                    className="bg-gradient-to-r from-[#1f6feb] to-[#38bdf8] h-full rounded-full"
                    style={{ width: `${item.pct * 4}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Daily Ingestion Profile */}
        <div className="rounded-lg bg-[#161b22] border border-[#30363d] p-5 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-2">
              <Layers className="h-4 w-4 text-[#3fb950]" />
              Knowledge Graph Serialization Status
            </h3>
            <p className="text-xs text-[#8b949e] mb-4">
              Dual W3C serialization pipeline exports both Turtle and JSON-LD on each sync cycle.
            </p>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-lg bg-[#0d1117] border border-[#30363d] flex items-center justify-between">
                <div>
                  <div className="font-semibold text-white">Turtle (.ttl) Triples</div>
                  <div className="text-[11px] text-[#8b949e]">data/output/enviromap_kg.ttl</div>
                </div>
                <span className="font-mono text-[#3fb950] font-bold">1,045,274</span>
              </div>

              <div className="p-3 rounded-lg bg-[#0d1117] border border-[#30363d] flex items-center justify-between">
                <div>
                  <div className="font-semibold text-white">JSON-LD Triples</div>
                  <div className="text-[11px] text-[#8b949e]">data/output/enviromap_kg.jsonld</div>
                </div>
                <span className="font-mono text-[#38bdf8] font-bold">1,045,274</span>
              </div>

              <div className="p-3 rounded-lg bg-[#0d1117] border border-[#30363d] flex items-center justify-between">
                <div>
                  <div className="font-semibold text-white">Total Export Time</div>
                  <div className="text-[11px] text-[#8b949e]">Autonomous Background Ingestion</div>
                </div>
                <span className="font-mono text-[#d29922] font-bold">45.1s</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Standards Ontology Registry */}
      <div className="rounded-lg bg-[#161b22] border border-[#30363d] p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-4">
          <BookOpen className="h-4 w-4 text-[#a371f7]" />
          Foundational Standards & Semantic Registries
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {ontologies.map((o, idx) => (
            <div key={idx} className="rounded-lg bg-[#0d1117] border border-[#30363d] p-3.5 text-xs">
              <div className="font-bold text-white text-sm">{o.name}</div>
              <div className="text-[#58a6ff] text-[11px] font-mono mt-0.5">{o.standard}</div>
              <div className="text-[#8b949e] text-[11px] mt-2 leading-relaxed">{o.desc}</div>
              <div className="mt-3 pt-2 border-t border-[#21262d] text-[10px] text-[#8b949e] font-mono truncate">
                {o.uri}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

