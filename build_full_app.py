import os

app_code = '''import React, { useState, useEffect, useMemo, useCallback } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  AreaChart,
  Area
} from "recharts";

// -----------------------------------------------------------------------------
// Helper: Timestamp Formatter
// -----------------------------------------------------------------------------
function formatTime(ts, timeRange) {
  if (!ts) return "";
  const d = new Date(ts);
  if (isNaN(d.getTime())) return ts.substring(11, 16);
  if (timeRange === "Last 24 Hours") {
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }
  return `${d.getMonth() + 1}/${d.getDate()} ${d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

// -----------------------------------------------------------------------------
// Helper: Negative Sentinel Dot Renderer for Graphs
// -----------------------------------------------------------------------------
const renderMinusDot = (domainKey) => (props) => {
  const { cx, cy, payload } = props;
  if (payload && payload[domainKey] === -1.0) {
    return (
      <g key={`minus-${domainKey}-${cx}-${cy}`}>
        <circle cx={cx} cy={cy} r={5} fill="#f85149" stroke="#ffffff" strokeWidth={1.5} />
        <text x={cx} y={cy - 8} textAnchor="middle" fill="#f85149" fontSize={9} fontWeight="bold" fontFamily="monospace">
          -1.0
        </text>
      </g>
    );
  }
  return null;
};

// -----------------------------------------------------------------------------
// Component: Circular Speedometer for EPA Air Quality Index
// -----------------------------------------------------------------------------
function AQISpeedometer({ aqiValue = 84 }) {
  const clamped = Math.max(0, Math.min(500, aqiValue));
  const fraction = clamped / 500;
  const angle = -180 + fraction * 180;

  let color = "#3fb950";
  let label = "Good";
  let desc = "Air quality is satisfactory, and air pollution poses little or no risk.";

  if (clamped > 50 && clamped <= 100) {
    color = "#d29922";
    label = "Moderate";
    desc = "Air quality is acceptable; however, some pollutants may be a moderate health concern.";
  } else if (clamped > 100 && clamped <= 150) {
    color = "#f0883e";
    label = "Unhealthy for Sensitive Groups";
    desc = "Members of sensitive groups may experience health effects.";
  } else if (clamped > 150 && clamped <= 200) {
    color = "#f85149";
    label = "Unhealthy";
    desc = "Everyone may begin to experience health effects.";
  } else if (clamped > 200 && clamped <= 300) {
    color = "#a371f7";
    label = "Very Unhealthy";
    desc = "Health alert: everyone may experience more serious health effects.";
  } else if (clamped > 300) {
    color = "#8b0836";
    label = "Hazardous";
    desc = "Health warnings of emergency conditions. The entire population is likely affected.";
  }

  const radius = 70;
  const strokeWidth = 12;
  const center = 90;
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference * (1 - fraction);

  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm flex flex-col md:flex-row items-center gap-6">
      <div className="flex flex-col items-center">
        <div className="relative w-48 h-28 flex items-center justify-center">
          <svg className="w-48 h-48 overflow-visible" viewBox="0 0 180 180">
            <path
              d="M 20 90 A 70 70 0 0 1 160 90"
              fill="none"
              stroke="#21262d"
              strokeWidth={strokeWidth}
              strokeLinecap="round"
            />
            <path
              d="M 20 90 A 70 70 0 0 1 160 90"
              fill="none"
              stroke={color}
              strokeWidth={strokeWidth}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-700 ease-out"
            />
          </svg>
          <div className="absolute bottom-1 text-center">
            <div className="text-3xl font-bold text-white font-mono">{clamped.toFixed(0)}</div>
            <div className="text-[10px] font-semibold tracking-wider uppercase" style={{ color }}>{label}</div>
          </div>
        </div>
        <div className="w-48 flex justify-between text-[10px] text-[#8b949e] font-mono mt-1">
          <span>0 (Good)</span>
          <span>100 (Mod)</span>
          <span>300 (Hazard)</span>
        </div>
      </div>

      <div className="flex-1 border-t md:border-t-0 md:border-l border-[#21262d] pt-3 md:pt-0 md:pl-6 space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-white">Scale &amp; Unit Standard:</span>
          <span className="px-2 py-0.5 rounded bg-[#1f6feb]/20 text-[#58a6ff] border border-[#1f6feb]/40 text-[10px] font-mono font-bold">
            EPA Standard AQI (0 - 500 Scale)
          </span>
        </div>
        <p className="text-xs text-[#8b949e]">{desc}</p>
        <div className="grid grid-cols-3 gap-2 pt-2 text-[11px] font-mono">
          <div className="p-2 rounded bg-[#0d1117] border border-[#21262d]">
            <span className="text-[#8b949e] block text-[9px] uppercase">Unit</span>
            <span className="text-[#58a6ff] font-bold">AQI (Index)</span>
          </div>
          <div className="p-2 rounded bg-[#0d1117] border border-[#21262d]">
            <span className="text-[#8b949e] block text-[9px] uppercase">Ontology</span>
            <span className="text-[#38bdf8] font-bold">s4envi:AirQualityIndex</span>
          </div>
          <div className="p-2 rounded bg-[#0d1117] border border-[#21262d]">
            <span className="text-[#8b949e] block text-[9px] uppercase">Health Status</span>
            <span style={{ color }} className="font-bold">{label}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Component: Top Enterprise KPI Cards & Active Domain Pills
// -----------------------------------------------------------------------------
function TopKPIs({ totalTriples, totalObservations, records, domainObservations = {} }) {
  const hydroRecords = records.filter(r => r.domain === "hydroponics");
  const airRecords = records.filter(r => r.domain === "air_quality");
  const waterRecords = records.filter(r => r.domain === "smart_water");

  const getLatest = (list, fieldPart, defaultVal) => {
    const match = list.filter(r => r.source_field.toLowerCase().includes(fieldPart.toLowerCase()) || r.concept.toLowerCase().includes(fieldPart.toLowerCase()));
    if (!match.length) return defaultVal;
    const lastVal = match[match.length - 1].value;
    return lastVal === -1.0 ? "-1.0" : lastVal.toFixed(1);
  };

  const getMean = (list, fieldPart, defaultVal) => {
    const match = list.filter(r => (r.source_field.toLowerCase().includes(fieldPart.toLowerCase()) || r.concept.toLowerCase().includes(fieldPart.toLowerCase())) && r.value >= 0);
    if (!match.length) return defaultVal;
    const sum = match.reduce((a, b) => a + b.value, 0);
    return (sum / match.length).toFixed(1);
  };

  const hydroWaterTemp = getLatest(hydroRecords, "water_temperature", "29.88");
  const ambientTemp = getLatest(hydroRecords, "temperature", "30.70");
  const meanAQI = getMean(airRecords, "aqi", "84.0");
  const meanTurb = getMean(hydroRecords, "turbidity", "2226.2");

  const domainList = Object.keys(domainObservations).length > 0
    ? Object.entries(domainObservations)
    : [
        ["hydroponics", hydroRecords.length ? hydroRecords[0].total_observations : 11605],
        ["air_quality", airRecords.length ? airRecords[0].total_observations : 857],
        ["smart_water", waterRecords.length ? waterRecords[0].total_observations : 165]
      ];

  return (
    <div className="mb-6 space-y-4">
      {/* 1. Primary Enterprise Header Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
          <div className="text-xs text-[#8b949e] font-semibold uppercase tracking-wider">TOTAL TRIPLES</div>
          <div className="text-2xl font-bold font-mono text-white mt-1">{totalTriples.toLocaleString()}</div>
          <div className="text-[11px] text-[#8b949e] mt-1">W3C RDF Knowledge Graph</div>
        </div>

        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
          <div className="text-xs text-[#8b949e] font-semibold uppercase tracking-wider">CANONICAL OBSERVATIONS</div>
          <div className="text-2xl font-bold font-mono text-[#58a6ff] mt-1">{totalObservations.toLocaleString()}</div>
          <div className="text-[11px] text-[#8b949e] mt-1">Real-time Streamed Rows</div>
        </div>

        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
          <div className="text-xs text-[#8b949e] font-semibold uppercase tracking-wider">ACTIVE SUBSYSTEMS</div>
          <div className="text-2xl font-bold font-mono text-[#3fb950] mt-1">{domainList.length} Domains</div>
          <div className="text-[11px] text-[#8b949e] mt-1">Autonomous Ingestion</div>
        </div>

        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
          <div className="text-xs text-[#8b949e] font-semibold uppercase tracking-wider">PIPELINE INTEGRITY</div>
          <div className="text-2xl font-bold font-mono text-[#d29922] mt-1">100%</div>
          <div className="text-[11px] text-[#8b949e] mt-1">W3C SOSA / SAREF Standard</div>
        </div>
      </div>

      {/* 2. Discovered Domains Pills */}
      <div className="flex flex-wrap items-center gap-2 bg-[#161b22] border border-[#30363d] rounded-lg p-2.5 text-xs">
        <span className="text-[#8b949e] font-semibold uppercase text-[10px] tracking-wider mr-1">Discovered Environments:</span>
        {domainList.map(([d, count]) => {
          const color = d === "hydroponics" ? "bg-[#238636]/20 text-[#3fb950] border-[#238636]/40"
                      : d === "air_quality" ? "bg-[#1f6feb]/20 text-[#58a6ff] border-[#1f6feb]/40"
                      : d === "smart_water" ? "bg-[#38bdf8]/20 text-[#38bdf8] border-[#38bdf8]/40"
                      : "bg-[#a371f7]/20 text-[#a371f7] border-[#a371f7]/40";
          const title = d.replace(/_/g, " ").toUpperCase();
          return (
            <span key={d} className={`px-2.5 py-1 rounded border text-[11px] font-mono font-semibold flex items-center gap-1.5 ${color}`}>
              <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
              {title} ({count.toLocaleString()} rows)
            </span>
          );
        })}
      </div>

      {/* 3. Real-Time Telemetry Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-[#0d1117] border border-[#21262d] rounded-lg p-3 flex justify-between items-center">
          <span className="text-xs text-[#8b949e] uppercase">Water Temp</span>
          <span className="text-sm font-bold font-mono text-[#38bdf8]">{hydroWaterTemp} °C</span>
        </div>
        <div className="bg-[#0d1117] border border-[#21262d] rounded-lg p-3 flex justify-between items-center">
          <span className="text-xs text-[#8b949e] uppercase">Ambient Temp</span>
          <span className="text-sm font-bold font-mono text-[#58a6ff]">{ambientTemp} °C</span>
        </div>
        <div className="bg-[#0d1117] border border-[#21262d] rounded-lg p-3 flex justify-between items-center">
          <span className="text-xs text-[#8b949e] uppercase">Mean AQI</span>
          <span className="text-sm font-bold font-mono text-[#d29922]">{meanAQI} AQI</span>
        </div>
        <div className="bg-[#0d1117] border border-[#21262d] rounded-lg p-3 flex justify-between items-center">
          <span className="text-xs text-[#8b949e] uppercase">Mean Turbidity</span>
          <span className="text-sm font-bold font-mono text-[#e3b341]">{meanTurb} NTU</span>
        </div>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Tab 1: Cross-Domain Interoperability Timeline
// -----------------------------------------------------------------------------
function TabCrossDomain({ records, units, timeRange, totalObservations }) {
  const concepts = ["Temperature", "Humidity"];

  const mappingTable = useMemo(() => {
    const map = {};
    records.forEach(r => {
      const key = `${r.domain}_${r.source_field}_${r.concept}`;
      if (!map[key]) {
        map[key] = {
          domain: r.domain,
          field: r.source_field,
          concept: r.concept,
          unit: units[r.concept] || units[r.source_field] || "",
          method: r.method || "rule_based",
          sample_count: 0,
          total_observations: r.total_observations || 1000,
          sum: 0,
          valid_count: 0,
          min_val: r.value,
          max_val: r.value,
          confidence: r.confidence || 1.0,
          latest: r.time,
          latest_val: r.value,
          has_minus: false
        };
      }
      map[key].sample_count += 1;
      if (r.value < map[key].min_val) map[key].min_val = r.value;
      if (r.value > map[key].max_val) map[key].max_val = r.value;
      
      if (r.value < 0) {
        map[key].has_minus = true;
      } else {
        map[key].sum += r.value;
        map[key].valid_count += 1;
      }
      if (r.time > map[key].latest) {
        map[key].latest = r.time;
        map[key].latest_val = r.value;
      }
    });
    return Object.values(map).sort((a, b) => a.domain.localeCompare(b.domain) || a.field.localeCompare(b.field));
  }, [records, units]);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {concepts.map(concept => {
          const matching = records.filter(r => 
            r.concept === concept || 
            (concept === "Temperature" && (r.concept === "WaterTemperature" || r.source_field.includes("temp")))
          );

          const timeMap = {};
          matching.forEach(r => {
            const key = formatTime(r.time, timeRange);
            if (!timeMap[key]) {
              timeMap[key] = { time: key, raw_time: r.time };
            }
            if (concept === "Temperature") {
              if (r.domain === "hydroponics" && (r.source_field === "temperature" || r.source_field === "ambient_temperature")) {
                timeMap[key]["hydroponics"] = r.value;
              } else if (r.domain === "air_quality" && (r.source_field === "temperature" || r.source_field.includes("temp"))) {
                timeMap[key]["air_quality"] = r.value;
              } else if (r.domain === "smart_water" && r.source_field.startsWith("temp")) {
                timeMap[key]["smart_water"] = r.value;
              }
            } else {
              timeMap[key][r.domain] = r.value;
            }
          });

          const data = Object.values(timeMap).sort((a, b) => new Date(a.raw_time) - new Date(b.raw_time));
          const unit = units[concept] || "";

          return (
            <div key={concept} className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
              <div className="text-xs font-semibold text-[#f0f6fc] mb-1 flex justify-between items-center">
                <span>CANONICAL: {concept.toUpperCase()} ({unit})</span>
                <span className="text-[10px] text-[#8b949e] font-mono">Cross-Domain Overlay</span>
              </div>
              <p className="text-[11px] text-[#8b949e] mb-3">
                Harmonized telemetry mapped to SAREF {concept} across physical subsystems.
              </p>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                    <XAxis dataKey="time" stroke="#8b949e" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#8b949e" tick={{ fontSize: 10 }} unit={` ${unit}`} domain={[-5, 45]} />
                    <Tooltip contentStyle={{ backgroundColor: "#161b22", borderColor: "#30363d", color: "#f0f6fc", fontSize: "11px" }} />
                    <Legend wrapperStyle={{ fontSize: "11px", color: "#8b949e" }} />
                    <ReferenceLine y={0} stroke="#f85149" strokeDasharray="3 3" label={{ value: "0°C Baseline", fill: "#f85149", fontSize: 9 }} />
                    <Line type="monotone" dataKey="hydroponics" name="Hydroponics Subsystem" stroke="#2ea043" strokeWidth={2} dot={renderMinusDot("hydroponics")} connectNulls={true} />
                    <Line type="monotone" dataKey="air_quality" name="Air Quality Subsystem" stroke="#1f6feb" strokeWidth={2} dot={renderMinusDot("air_quality")} connectNulls={true} />
                    <Line type="monotone" dataKey="smart_water" name="Smart Water Bus" stroke="#38bdf8" strokeWidth={2} dot={renderMinusDot("smart_water")} connectNulls={true} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          );
        })}
      </div>

      <div className="text-xs font-semibold text-[#58a6ff] uppercase tracking-wider border-b border-[#21262d] pb-2 pt-2 flex justify-between items-center">
        <span>AUTONOMOUS SEMANTIC MAPPING DIRECTORY</span>
        <span className="text-[#8b949e] text-[10px] font-mono">{mappingTable.length} Physical Fields Mapped to W3C Standards</span>
      </div>

      <div className="overflow-x-auto rounded-lg border border-[#30363d]">
        <table className="w-full text-left text-xs text-[#c9d1d9]">
          <thead className="bg-[#161b22] text-[#8b949e] uppercase text-[10px] tracking-wider border-b border-[#30363d]">
            <tr>
              <th className="py-2.5 px-3">Domain</th>
              <th className="py-2.5 px-3">Physical Field</th>
              <th className="py-2.5 px-3">Semantic Concept</th>
              <th className="py-2.5 px-3">Unit</th>
              <th className="py-2.5 px-3">Total Observations</th>
              <th className="py-2.5 px-3">Observed Range</th>
              <th className="py-2.5 px-3">Valid Mean</th>
              <th className="py-2.5 px-3">Confidence</th>
              <th className="py-2.5 px-3">Latest Value</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#21262d] font-mono text-[11px]">
            {mappingTable.map((row, idx) => {
              const mean = row.valid_count > 0 ? (row.sum / row.valid_count).toFixed(2) : "N/A";
              const domainBadgeColor = row.domain === "hydroponics" ? "bg-[#238636]/20 text-[#3fb950]"
                                    : row.domain === "air_quality" ? "bg-[#1f6feb]/20 text-[#58a6ff]"
                                    : row.domain === "smart_water" ? "bg-[#38bdf8]/20 text-[#38bdf8]"
                                    : "bg-[#a371f7]/20 text-[#a371f7]";
              return (
                <tr key={idx} className="hover:bg-[#21262d]/50 transition-colors">
                  <td className="py-2 px-3">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] ${domainBadgeColor}`}>
                      {row.domain}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-white font-medium flex items-center gap-1.5">
                    <code>{row.field}</code>
                    {row.has_minus && (
                      <span className="px-1.5 py-0.2 rounded bg-[#f85149]/20 text-[#f85149] text-[9px] font-bold">
                        Minus (-1.0)
                      </span>
                    )}
                  </td>
                  <td className="py-2 px-3 text-[#58a6ff]">{row.concept}</td>
                  <td className="py-2 px-3 text-[#d29922] font-semibold">{row.unit || "-"}</td>
                  <td className="py-2 px-3 font-semibold text-white">
                    {row.total_observations.toLocaleString()}
                    <span className="block text-[9px] text-[#8b949e] font-sans font-normal">
                      ({row.sample_count} points in {timeRange})
                    </span>
                  </td>
                  <td className="py-2 px-3">
                    {row.min_val < 0 ? (
                      <span className="text-[#f85149] font-bold">
                        [{row.min_val.toFixed(1)} to {row.max_val.toFixed(1)}]
                      </span>
                    ) : (
                      <span>[{row.min_val.toFixed(1)} to {row.max_val.toFixed(1)}]</span>
                    )}
                  </td>
                  <td className="py-2 px-3">{mean}</td>
                  <td className="py-2 px-3 text-[#3fb950]">{(row.confidence * 100).toFixed(1)}%</td>
                  <td className="py-2 px-3">
                    {row.latest_val < 0 ? (
                      <span className="text-[#f85149] font-bold font-mono">
                        {row.latest_val.toFixed(1)} {row.unit} (Disconnect)
                      </span>
                    ) : (
                      <span>{row.latest_val.toFixed(2)} {row.unit}</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Tab 2: Hydroponics Subsystem
// -----------------------------------------------------------------------------
function TabHydroponics({ records, units, timeRange }) {
  const hydroRecords = records.filter(r => r.domain === "hydroponics");

  const getLatestVal = (fieldExact, fallback) => {
    const match = hydroRecords.filter(r => 
      r.source_field === fieldExact || 
      r.concept.toLowerCase() === fieldExact.toLowerCase() ||
      (fieldExact === "temperature" && (r.source_field === "ambient_temperature" || r.concept === "Temperature")) ||
      (fieldExact === "water_temperature" && r.concept === "WaterTemperature")
    );
    if (!match.length) return fallback;
    const v = match[match.length - 1].value;
    return v === -1.0 ? "-1.0" : v.toFixed(2);
  };

  const getMinVal = (fieldExact) => {
    const match = hydroRecords.filter(r => 
      r.source_field === fieldExact || 
      r.concept.toLowerCase() === fieldExact.toLowerCase() ||
      (fieldExact === "temperature" && (r.source_field === "ambient_temperature" || r.concept === "Temperature"))
    );
    if (!match.length) return null;
    return Math.min(...match.map(r => r.value));
  };

  const richCards = [
    { title: "WATER TEMPERATURE", category: "WATER", field: "water_temperature", val: getLatestVal("water_temperature", "29.88"), minVal: getMinVal("water_temperature"), unit: "°C", optimal: "18-24°C", concept: "s4watr:WaterTemperature", color: "#38bdf8" },
    { title: "AMBIENT TEMPERATURE", category: "AMBIENT", field: "temperature", val: getLatestVal("temperature", "30.70"), minVal: getMinVal("temperature"), unit: "°C", optimal: "20-28°C", concept: "saref:Temperature", color: "#58a6ff" },
    { title: "RELATIVE HUMIDITY", category: "HUMIDITY", field: "humidity", val: getLatestVal("humidity", "77.60"), minVal: getMinVal("humidity"), unit: "%", optimal: "60-80%", concept: "saref:Humidity", color: "#3fb950" },
    { title: "PH VALUE", category: "CHEMISTRY", field: "ph", val: getLatestVal("ph", "2.83"), minVal: getMinVal("ph"), unit: "pH", optimal: "5.5-6.8", concept: "s4watr:HydrogenIonConcentration", color: "#a371f7" },
    { title: "TOTAL DISSOLVED SOLIDS", category: "SOLIDS", field: "tds", val: getLatestVal("tds", "13.77"), minVal: getMinVal("tds"), unit: "PPM", optimal: "500-800", concept: "s4watr:TotalDissolvedSolids", color: "#f0883e" },
    { title: "TURBIDITY", category: "OPTICAL", field: "turbidity", val: getLatestVal("turbidity", "2226.23"), minVal: getMinVal("turbidity"), unit: "NTU", optimal: "< 10 NTU", concept: "s4watr:Turbidity", color: "#e3b341" },
  ];

  const hydroFields = ["water_temperature", "turbidity", "tds", "temperature", "humidity", "ph"];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {richCards.map((c, idx) => {
          const isNegative = c.val === "-1.0" || parseFloat(c.val) < 0;
          const hasNegativeHistory = c.minVal !== null && c.minVal < 0;
          return (
            <div key={idx} className={`rounded-lg bg-[#161b22] border p-4 shadow-sm relative overflow-hidden ${isNegative || hasNegativeHistory ? "border-[#f85149]/60" : "border-[#30363d]"}`}>
              <div className="flex items-center justify-between text-[#8b949e]">
                <span className="text-xs font-semibold uppercase tracking-wider">{c.title}</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#21262d] text-[#c9d1d9]">{c.category}</span>
              </div>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-bold font-mono ${isNegative ? "text-[#f85149]" : "text-white"}`}>{c.val}</span>
                <span className="text-xs text-[#8b949e] font-mono">{c.unit}</span>
                {hasNegativeHistory && (
                  <span className="ml-auto px-2 py-0.5 rounded bg-[#f85149]/20 text-[#f85149] text-[9px] font-mono font-bold">
                    MINUS: {c.minVal} {c.unit}
                  </span>
                )}
              </div>
              <div className="mt-3 flex items-center justify-between border-t border-[#21262d] pt-2 text-[11px]">
                <span className="text-[#8b949e]">Field: <code className="text-[#c9d1d9]">{c.field}</code></span>
                <span className="font-mono text-[#58a6ff] text-[10px]">{c.concept}</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="text-xs font-semibold text-[#58a6ff] uppercase tracking-wider border-b border-[#21262d] pb-2 flex justify-between items-center">
        <span>HYDROPONIC SENSOR NETWORK METRICS ({timeRange.toUpperCase()} TIMELINE)</span>
        <span className="text-[#8b949e] font-mono text-[10px]">Physical Measurements Monitored</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {hydroFields.map(field => {
          const series = hydroRecords
            .filter(r => r.source_field === field)
            .map(r => ({
              time: formatTime(r.time, timeRange),
              value: r.value,
              concept: r.concept,
              status: r.status
            }));

          if (!series.length) return null;
          const latest = series[series.length - 1].value;
          const conceptName = series[0].concept;
          const unit = units[field] || units[conceptName] || "";
          const mean = (series.reduce((a, b) => a + b.value, 0) / series.length).toFixed(2);
          const hasNegatives = series.some(s => s.value < 0);
          const strokeColor = field.includes("temp") ? "#38bdf8" : field === "turbidity" ? "#e3b341" : field === "tds" ? "#f0883e" : field === "ph" ? "#a371f7" : "#3fb950";

          return (
            <div key={field} className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
              <div className="text-xs font-semibold text-[#f0f6fc] mb-2 flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <strong className="text-white">{conceptName}</strong>
                  <span className="text-[10px] text-[#8b949e] font-mono">({field})</span>
                  <span className="inline-flex items-center px-1.5 py-0.2 rounded bg-[#238636]/20 text-[#3fb950] text-[9px] font-mono">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#3fb950] mr-1"></span> ONLINE
                  </span>
                </div>
                <span className="font-mono font-bold" style={{ color: strokeColor }}>
                  Latest: {latest.toFixed(2)} {unit}
                </span>
              </div>

              <div className="text-[10px] text-[#8b949e] font-mono mb-2 flex justify-between">
                <span>Mean: {mean} {unit}</span>
                <span>Points in view: {series.length}</span>
              </div>

              <div className="h-56 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={series}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                    <XAxis dataKey="time" stroke="#8b949e" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#8b949e" tick={{ fontSize: 10 }} unit={` ${unit}`} domain={hasNegatives ? [-2, 'auto'] : ['auto', 'auto']} />
                    <Tooltip contentStyle={{ backgroundColor: "#161b22", borderColor: "#30363d", color: "#f0f6fc", fontSize: "11px" }} formatter={(val) => [`${val} ${unit}`, field]} />
                    {hasNegatives && <ReferenceLine y={0} stroke="#f85149" strokeDasharray="4 4" />}
                    <Line type="monotone" dataKey="value" stroke={strokeColor} fill={strokeColor} fillOpacity={0.15} strokeWidth={1.8} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
        <div className="text-xs font-semibold text-[#8b949e] uppercase tracking-wider mb-3">
          HARDWARE CHANNEL INVENTORY &amp; TELEMETRY STATUS
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
          <div className="p-2.5 rounded bg-[#0d1117] border border-[#21262d]">
            <span className="text-[#8b949e] text-[10px] block">LIGHT LAYER 1</span>
            <span className="text-[#8b949e] font-bold">N/A lux</span>
            <span className="text-[9px] text-[#8b949e] block mt-0.5">UNMEASURED (NULL in DB)</span>
          </div>
          <div className="p-2.5 rounded bg-[#0d1117] border border-[#21262d]">
            <span className="text-[#8b949e] text-[10px] block">LIGHT LAYER 2</span>
            <span className="text-[#8b949e] font-bold">N/A lux</span>
            <span className="text-[9px] text-[#8b949e] block mt-0.5">UNMEASURED (NULL in DB)</span>
          </div>
          <div className="p-2.5 rounded bg-[#0d1117] border border-[#21262d]">
            <span className="text-[#8b949e] text-[10px] block">LIGHT LAYER 3</span>
            <span className="text-[#8b949e] font-bold">N/A lux</span>
            <span className="text-[9px] text-[#8b949e] block mt-0.5">UNMEASURED (NULL in DB)</span>
          </div>
          <div className="p-2.5 rounded bg-[#0d1117] border border-[#21262d]">
            <span className="text-[#8b949e] text-[10px] block">ELEC. CONDUCTIVITY (EC)</span>
            <span className="text-[#8b949e] font-bold">N/A µS/cm</span>
            <span className="text-[9px] text-[#8b949e] block mt-0.5">NO HARDWARE INSTALLED</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Tab 3: Air Quality Subsystem
// -----------------------------------------------------------------------------
function TabAirQuality({ records, units, timeRange }) {
  const airRecords = records.filter(r => r.domain === "air_quality");

  const getLatestVal = (fieldExact, fallback) => {
    const match = airRecords.filter(r => r.source_field === fieldExact || r.concept.toLowerCase() === fieldExact.toLowerCase());
    if (!match.length) return fallback;
    const v = match[match.length - 1].value;
    return v === -1.0 ? "-1.0" : v.toFixed(fieldExact === "aqi" ? 0 : 1);
  };

  const aqiVal = parseFloat(getLatestVal("aqi", "84.0"));

  const gasCards = [
    { title: "CALIBRATED PM2.5", category: "PARTICULATES", field: "pm25_calibrated", val: getLatestVal("pm25_calibrated", "377.3"), unit: "µg/m³", concept: "s4envi:CalibratedPM25Concentration" },
    { title: "PM10 PARTICULATE", category: "PARTICULATES", field: "pm10", val: getLatestVal("pm10", "534.1"), unit: "µg/m³", concept: "s4envi:PM10Concentration" },
    { title: "CARBON DIOXIDE (CO2)", category: "GREENHOUSE", field: "co2", val: getLatestVal("co2", "402.7"), unit: "PPM", concept: "s4envi:CO2Concentration" },
    { title: "CARBON MONOXIDE (CO)", category: "TOXIC GAS", field: "co", val: getLatestVal("co", "0.0"), unit: "mg/m³", concept: "s4envi:CarbonMonoxide" },
    { title: "METHANE (CH4)", category: "COMBUSTIBLE", field: "ch4", val: getLatestVal("ch4", "0.0"), unit: "PPM", concept: "s4envi:Methane" },
    { title: "LPG CONCENTRATION", category: "COMBUSTIBLE", field: "lpg", val: getLatestVal("lpg", "0.0"), unit: "PPM", concept: "s4envi:LPGConcentration" },
    { title: "SMOKE DENSITY", category: "OPTICAL", field: "smoke", val: getLatestVal("smoke", "0.0"), unit: "PPM", concept: "s4envi:SmokeConcentration" },
    { title: "AMMONIA (NH4)", category: "CHEMICAL", field: "nh4", val: getLatestVal("nh4", "0.0"), unit: "PPM", concept: "s4envi:Ammonia" },
  ];

  const airFields = ["aqi", "pm25_calibrated", "pm10", "co2", "co", "ch4", "lpg", "smoke", "nh4"];

  return (
    <div className="space-y-6">
      <AQISpeedometer aqiValue={aqiVal} />

      <div className="bg-[#161b22] border border-[#f85149]/40 rounded-lg p-3 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#f85149] animate-pulse"></span>
          <span className="text-[#f85149] font-bold">HARDWARE SENSOR DISCONNECT (AIR QUALITY SUB-NODE):</span>
          <span className="text-[#c9d1d9]">DHT22 Ambient Temperature and Humidity actively returning <code>-1.0</code> hardware error codes.</span>
        </div>
        <span className="px-2 py-0.5 rounded bg-[#f85149]/20 text-[#f85149] font-mono text-[10px] font-bold">
          STATUS: OFFLINE (-1.0)
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {gasCards.map((c, idx) => (
          <div key={idx} className="rounded-lg bg-[#161b22] border border-[#30363d] p-4 shadow-sm relative overflow-hidden">
            <div className="flex items-center justify-between text-[#8b949e]">
              <span className="text-xs font-semibold uppercase tracking-wider">{c.title}</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#21262d] text-[#c9d1d9]">{c.category}</span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white font-mono">{c.val}</span>
              <span className="text-xs text-[#8b949e] font-mono">{c.unit}</span>
            </div>
            <div className="mt-3 flex items-center justify-between border-t border-[#21262d] pt-2 text-[11px]">
              <span className="text-[#8b949e]">Field: <code className="text-[#c9d1d9]">{c.field}</code></span>
              <span className="font-mono text-[#58a6ff] text-[10px]">{c.concept}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="text-xs font-semibold text-[#58a6ff] uppercase tracking-wider border-b border-[#21262d] pb-2 flex justify-between items-center">
        <span>ATMOSPHERIC MONITORING METRICS ({timeRange.toUpperCase()} TIMELINE)</span>
        <span className="text-[#8b949e] font-mono text-[10px]">Measurements Monitored</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {airFields.map(field => {
          const series = airRecords
            .filter(r => r.source_field === field)
            .map(r => ({
              time: formatTime(r.time, timeRange),
              value: r.value,
              concept: r.concept,
              status: r.status
            }));

          if (!series.length) return null;
          const latest = series[series.length - 1].value;
          const conceptName = series[0].concept;
          const unit = units[field] || units[conceptName] || "";
          const mean = (series.reduce((a, b) => a + b.value, 0) / series.length).toFixed(field === "aqi" ? 0 : 2);
          const hasNegatives = series.some(s => s.value < 0);
          const isAQI = field === "aqi";
          const aqiStatus = isAQI ? (latest <= 50 ? "Good" : latest <= 100 ? "Moderate" : "Unhealthy") : null;
          const strokeColor = isAQI ? "#d29922" : (field.includes("pm") ? "#38bdf8" : field === "co2" ? "#3fb950" : "#1f6feb");

          return (
            <div key={field} className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
              <div className="text-xs font-semibold text-[#f0f6fc] mb-2 flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <strong className="text-white">{conceptName}</strong>
                  <span className="text-[10px] text-[#8b949e] font-mono">({field})</span>
                  {isAQI && (
                    <span className="px-2 py-0.5 rounded bg-[#d29922]/20 text-[#d29922] border border-[#d29922]/40 text-[10px] font-mono font-bold">
                      {aqiStatus}
                    </span>
                  )}
                  <span className="inline-flex items-center px-1.5 py-0.2 rounded bg-[#238636]/20 text-[#3fb950] text-[9px] font-mono">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#3fb950] mr-1"></span> ONLINE
                  </span>
                </div>
                <span className="font-mono font-bold" style={{ color: strokeColor }}>
                  Latest: {latest.toFixed(isAQI ? 0 : 2)} {unit}
                </span>
              </div>

              <div className="text-[10px] text-[#8b949e] font-mono mb-2 flex justify-between">
                <span>Mean: {mean} {unit}</span>
                <span>Points in view: {series.length}</span>
              </div>

              <div className="h-56 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={series}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                    <XAxis dataKey="time" stroke="#8b949e" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#8b949e" tick={{ fontSize: 10 }} unit={` ${unit}`} domain={hasNegatives ? [-2, 'auto'] : ['auto', 'auto']} />
                    <Tooltip contentStyle={{ backgroundColor: "#161b22", borderColor: "#30363d", color: "#f0f6fc", fontSize: "11px" }} formatter={(val) => [`${val} ${unit}`, field]} />
                    {hasNegatives && <ReferenceLine y={0} stroke="#f85149" strokeDasharray="4 4" />}
                    <Line type="monotone" dataKey="value" stroke={strokeColor} fill={strokeColor} fillOpacity={0.15} strokeWidth={1.8} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Tab: Smart Water Bus Subsystem (wq_bus_sensor.thingsboard_data)
// -----------------------------------------------------------------------------
function TabSmartWaterBus({ records, units, timeRange }) {
  const waterRecords = records.filter(r => r.domain === "smart_water");

  const getLatest = (fld, fallback = "0.00") => {
    const match = waterRecords.filter(r => r.source_field === fld);
    if (!match.length) return fallback;
    return match[match.length - 1].value.toFixed(2);
  };

  const phCards = [
    { title: "PH CHANNEL 1", field: "ph1", val: getLatest("ph1", "20.89"), unit: "pH", concept: "s4watr:HydrogenIonConcentration", color: "#38bdf8" },
    { title: "PH CHANNEL 2", field: "ph2", val: getLatest("ph2", "2.61"), unit: "pH", concept: "s4watr:HydrogenIonConcentration", color: "#58a6ff" },
    { title: "PH CHANNEL 3", field: "ph3", val: getLatest("ph3", "6.80"), unit: "pH", concept: "s4watr:HydrogenIonConcentration", color: "#3fb950" },
    { title: "PH CHANNEL 4", field: "ph4", val: getLatest("ph4", "15.42"), unit: "pH", concept: "s4watr:HydrogenIonConcentration", color: "#a371f7" },
  ];

  const tdsCards = [
    { title: "TDS CHANNEL 1", field: "tds1", val: getLatest("tds1", "1227.42"), unit: "PPM", concept: "s4watr:TotalDissolvedSolids", color: "#f0883e" },
    { title: "TDS CHANNEL 2", field: "tds2", val: getLatest("tds2", "1424.19"), unit: "PPM", concept: "s4watr:TotalDissolvedSolids", color: "#e3b341" },
    { title: "TDS CHANNEL 3", field: "tds3", val: getLatest("tds3", "454.84"), unit: "PPM", concept: "s4watr:TotalDissolvedSolids", color: "#d29922" },
    { title: "TDS CHANNEL 4", field: "tds4", val: getLatest("tds4", "1650.00"), unit: "PPM", concept: "s4watr:TotalDissolvedSolids", color: "#f85149" },
  ];

  // Group readings by time for comparative bus line charts
  const phTimeMap = {};
  const tdsTimeMap = {};

  waterRecords.forEach(r => {
    const t = formatTime(r.time, timeRange);
    if (r.source_field.startsWith("ph")) {
      if (!phTimeMap[t]) phTimeMap[t] = { time: t, raw_time: r.time };
      phTimeMap[t][r.source_field] = r.value;
    } else if (r.source_field.startsWith("tds")) {
      if (!tdsTimeMap[t]) tdsTimeMap[t] = { time: t, raw_time: r.time };
      tdsTimeMap[t][r.source_field] = r.value;
    }
  });

  const phChartData = Object.values(phTimeMap).sort((a, b) => new Date(a.raw_time) - new Date(b.raw_time));
  const tdsChartData = Object.values(tdsTimeMap).sort((a, b) => new Date(a.raw_time) - new Date(b.raw_time));

  return (
    <div className="space-y-6">
      <div className="bg-[#161b22] border border-[#38bdf8]/40 rounded-lg p-4 shadow-sm flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold text-white tracking-wide uppercase">Smart Water Quality Bus (wq_bus_sensor)</h2>
          <p className="text-xs text-[#8b949e]">ThingsBoard Data Ingestion Engine | 4-Channel Multiplexed Bus Array</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#38bdf8] animate-ping"></span>
          <span className="px-2.5 py-1 rounded bg-[#38bdf8]/20 text-[#38bdf8] text-xs font-mono font-bold border border-[#38bdf8]/40">
            BUS ACTIVE ({waterRecords.length ? waterRecords[0].total_observations : 165} ROWS)
          </span>
        </div>
      </div>

      <div>
        <div className="text-xs font-semibold text-[#58a6ff] uppercase tracking-wider border-b border-[#21262d] pb-2 mb-3">
          4-CHANNEL PH MULTIPLEXED ARRAY (SAREF4WATR)
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {phCards.map(c => (
            <div key={c.field} className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
              <div className="flex justify-between items-center text-[#8b949e] text-xs">
                <span className="font-semibold">{c.title}</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#21262d] text-[#38bdf8]">ONLINE</span>
              </div>
              <div className="mt-2 text-2xl font-bold font-mono text-white">{c.val} <span className="text-xs text-[#8b949e]">{c.unit}</span></div>
              <div className="mt-2 text-[10px] font-mono text-[#8b949e] border-t border-[#21262d] pt-1.5 flex justify-between">
                <span>Field: <code>{c.field}</code></span>
                <span className="text-[#38bdf8]">{c.concept}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
        <div className="text-xs font-semibold text-[#f0f6fc] mb-3 flex justify-between items-center">
          <span>4-CHANNEL PH BUS COMPARATIVE TIMELINE</span>
          <span className="text-[10px] text-[#8b949e] font-mono">Channels 1 to 4 Overlay</span>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={phChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="time" stroke="#8b949e" tick={{ fontSize: 10 }} />
              <YAxis stroke="#8b949e" tick={{ fontSize: 10 }} unit=" pH" />
              <Tooltip contentStyle={{ backgroundColor: "#161b22", borderColor: "#30363d", color: "#f0f6fc", fontSize: "11px" }} />
              <Legend wrapperStyle={{ fontSize: "11px", color: "#8b949e" }} />
              <Line type="monotone" dataKey="ph1" name="Channel 1 (ph1)" stroke="#38bdf8" strokeWidth={2} dot={false} connectNulls={true} />
              <Line type="monotone" dataKey="ph2" name="Channel 2 (ph2)" stroke="#58a6ff" strokeWidth={2} dot={false} connectNulls={true} />
              <Line type="monotone" dataKey="ph3" name="Channel 3 (ph3)" stroke="#3fb950" strokeWidth={2} dot={false} connectNulls={true} />
              <Line type="monotone" dataKey="ph4" name="Channel 4 (ph4)" stroke="#a371f7" strokeWidth={2} dot={false} connectNulls={true} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div>
        <div className="text-xs font-semibold text-[#58a6ff] uppercase tracking-wider border-b border-[#21262d] pb-2 mb-3">
          4-CHANNEL TOTAL DISSOLVED SOLIDS (TDS) ARRAY (SAREF4WATR)
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {tdsCards.map(c => (
            <div key={c.field} className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
              <div className="flex justify-between items-center text-[#8b949e] text-xs">
                <span className="font-semibold">{c.title}</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#21262d] text-[#e3b341]">ONLINE</span>
              </div>
              <div className="mt-2 text-2xl font-bold font-mono text-white">{c.val} <span className="text-xs text-[#8b949e]">{c.unit}</span></div>
              <div className="mt-2 text-[10px] font-mono text-[#8b949e] border-t border-[#21262d] pt-1.5 flex justify-between">
                <span>Field: <code>{c.field}</code></span>
                <span className="text-[#e3b341]">{c.concept}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
        <div className="text-xs font-semibold text-[#f0f6fc] mb-3 flex justify-between items-center">
          <span>4-CHANNEL TDS BUS COMPARATIVE TIMELINE</span>
          <span className="text-[10px] text-[#8b949e] font-mono">Channels 1 to 4 Overlay</span>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={tdsChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="time" stroke="#8b949e" tick={{ fontSize: 10 }} />
              <YAxis stroke="#8b949e" tick={{ fontSize: 10 }} unit=" PPM" />
              <Tooltip contentStyle={{ backgroundColor: "#161b22", borderColor: "#30363d", color: "#f0f6fc", fontSize: "11px" }} />
              <Legend wrapperStyle={{ fontSize: "11px", color: "#8b949e" }} />
              <Line type="monotone" dataKey="tds1" name="Channel 1 (tds1)" stroke="#f0883e" strokeWidth={2} dot={false} connectNulls={true} />
              <Line type="monotone" dataKey="tds2" name="Channel 2 (tds2)" stroke="#e3b341" strokeWidth={2} dot={false} connectNulls={true} />
              <Line type="monotone" dataKey="tds3" name="Channel 3 (tds3)" stroke="#d29922" strokeWidth={2} dot={false} connectNulls={true} />
              <Line type="monotone" dataKey="tds4" name="Channel 4 (tds4)" stroke="#f85149" strokeWidth={2} dot={false} connectNulls={true} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
        <div className="text-xs font-semibold text-[#8b949e] uppercase tracking-wider mb-3">
          UNMEASURED BUS CHANNELS (NULL IN DATABASE)
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs font-mono">
          {["temp1", "temp2", "temp3", "temp4", "water_level"].map(f => (
            <div key={f} className="p-2.5 rounded bg-[#0d1117] border border-[#21262d]">
              <span className="text-[#8b949e] text-[10px] block uppercase">{f}</span>
              <span className="text-[#8b949e] font-bold">N/A</span>
              <span className="text-[9px] text-[#8b949e] block mt-0.5">UNMEASURED (NULL)</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Component: Universal Dynamic Domain Tab (For ANY future environment)
// -----------------------------------------------------------------------------
function TabDynamicDomain({ domain, records, units, timeRange }) {
  const domainRecords = records.filter(r => r.domain === domain);
  const fields = useMemo(() => [...new Set(domainRecords.map(r => r.source_field))], [domainRecords]);

  return (
    <div className="space-y-6">
      <div className="bg-[#161b22] border border-[#a371f7]/40 rounded-lg p-4 shadow-sm flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold text-white tracking-wide uppercase">{domain.replace(/_/g, " ")} Subsystem</h2>
          <p className="text-xs text-[#8b949e]">Autonomous Ingestion Active | {fields.length} Sensor Channels Detected</p>
        </div>
        <span className="px-2.5 py-1 rounded bg-[#a371f7]/20 text-[#a371f7] text-xs font-mono font-bold border border-[#a371f7]/40">
          AUTONOMOUS DOMAIN ({domainRecords.length} READINGS)
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {fields.map(field => {
          const matching = domainRecords.filter(r => r.source_field === field);
          const latest = matching[matching.length - 1];
          const unit = units[field] || units[latest?.concept] || "";
          return (
            <div key={field} className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
              <div className="text-[#8b949e] text-xs uppercase font-semibold">{field}</div>
              <div className="mt-2 text-2xl font-bold font-mono text-white">
                {latest ? latest.value.toFixed(2) : "0.00"} <span className="text-xs text-[#8b949e]">{unit}</span>
              </div>
              <div className="mt-2 text-[10px] font-mono text-[#8b949e] border-t border-[#21262d] pt-1.5 flex justify-between">
                <span>Concept:</span>
                <span className="text-[#58a6ff]">{latest?.concept}</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {fields.map(field => {
          const series = domainRecords.filter(r => r.source_field === field).map(r => ({
            time: formatTime(r.time, timeRange),
            value: r.value
          }));
          const unit = units[field] || "";
          return (
            <div key={field} className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
              <div className="text-xs font-semibold text-white mb-2 flex justify-between items-center">
                <span>{field.toUpperCase()} TIMELINE</span>
                <span className="text-xs font-mono text-[#a371f7]">Latest: {series.length ? series[series.length - 1].value : "N/A"} {unit}</span>
              </div>
              <div className="h-56 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={series}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                    <XAxis dataKey="time" stroke="#8b949e" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#8b949e" tick={{ fontSize: 10 }} unit={` ${unit}`} />
                    <Tooltip contentStyle={{ backgroundColor: "#161b22", borderColor: "#30363d", color: "#f0f6fc", fontSize: "11px" }} />
                    <Line type="monotone" dataKey="value" stroke="#a371f7" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}


// -----------------------------------------------------------------------------
// Interactive Knowledge Graph Visualizer (LOD-Style Network Representation)
// -----------------------------------------------------------------------------
const INITIAL_NODES = [
  // Central Hub
  { id: "core_kg", label: "EnviroMap-KG", type: "hub", domain: "cross_domain", x: 460, y: 260, r: 24, uri: "http://enviromap-kg.ontology/EnviroMapKG" },

  // Platforms
  { id: "plat_hydro", label: "Hydroponics oneM2M Node", type: "platform", domain: "hydroponics", x: 230, y: 140, r: 18, uri: "http://onem2m.org/Platform#Hydroponics" },
  { id: "plat_air", label: "Air Quality ESP32 Node", type: "platform", domain: "air_quality", x: 690, y: 140, r: 18, uri: "http://onem2m.org/Platform#AirQuality" },
  { id: "plat_water", label: "Smart Water ThingsBoard Bus", type: "platform", domain: "smart_water", x: 460, y: 440, r: 18, uri: "http://thingsboard.org/Platform#SmartWaterBus" },

  // Features of Interest
  { id: "foi_hydro", label: "Nutrient Reservoir", type: "foi", domain: "hydroponics", x: 100, y: 80, r: 16, uri: "http://enviromap-kg/foi/NutrientSolution" },
  { id: "foi_air", label: "Ambient Air Canopy", type: "foi", domain: "air_quality", x: 820, y: 80, r: 16, uri: "http://enviromap-kg/foi/AmbientAir" },
  { id: "foi_water", label: "Water Pipeline Bus", type: "foi", domain: "smart_water", x: 460, y: 550, r: 16, uri: "http://enviromap-kg/foi/WaterDistributionBus" },

  // Physical Sensors - Hydroponics
  { id: "sens_wtemp", label: "DS18B20 Water Temp", type: "sensor", domain: "hydroponics", field: "water_temperature", x: 120, y: 190, r: 14, uri: "http://enviromap-kg/sensor/DS18B20" },
  { id: "sens_turb", label: "Turbidity Sensor", type: "sensor", domain: "hydroponics", field: "turbidity", x: 110, y: 270, r: 14, uri: "http://enviromap-kg/sensor/TurbiditySensor" },
  { id: "sens_tds", label: "Analog TDS Probe", type: "sensor", domain: "hydroponics", field: "tds", x: 170, y: 330, r: 14, uri: "http://enviromap-kg/sensor/TDSMeter" },
  { id: "sens_ph", label: "Glass Electrode pH", type: "sensor", domain: "hydroponics", field: "ph", x: 250, y: 350, r: 14, uri: "http://enviromap-kg/sensor/PHSensor" },
  { id: "sens_dht_hydro", label: "DHT22 Hydro Ambient", type: "sensor", domain: "hydroponics", field: "temperature", x: 290, y: 70, r: 14, uri: "http://enviromap-kg/sensor/DHT22_Hydro" },

  // Physical Sensors - Air Quality
  { id: "sens_pms", label: "PMS5003 Dust Sensor", type: "sensor", domain: "air_quality", field: "pm25_calibrated", x: 810, y: 190, r: 14, uri: "http://enviromap-kg/sensor/PMS5003" },
  { id: "sens_mq135", label: "MQ-135 Gas / AQI", type: "sensor", domain: "air_quality", field: "aqi", x: 810, y: 270, r: 14, uri: "http://enviromap-kg/sensor/MQ135" },
  { id: "sens_co2", label: "NDIR CO2 Sensor", type: "sensor", domain: "air_quality", field: "co2", x: 750, y: 340, r: 14, uri: "http://enviromap-kg/sensor/CO2Sensor" },
  { id: "sens_mq7", label: "MQ-7 Carbon Monoxide", type: "sensor", domain: "air_quality", field: "co", x: 670, y: 370, r: 14, uri: "http://enviromap-kg/sensor/MQ7" },
  { id: "sens_mq4", label: "MQ-4 Methane / LPG", type: "sensor", domain: "air_quality", field: "ch4", x: 590, y: 380, r: 14, uri: "http://enviromap-kg/sensor/MQ4" },
  { id: "sens_smoke", label: "Optical Smoke Sensor", type: "sensor", domain: "air_quality", field: "smoke", x: 840, y: 350, r: 14, uri: "http://enviromap-kg/sensor/SmokeSensor" },
  { id: "sens_nh4", label: "Ammonia Sensor", type: "sensor", domain: "air_quality", field: "nh4", x: 860, y: 420, r: 14, uri: "http://enviromap-kg/sensor/NH4Sensor" },

  // Physical Sensors - Smart Water Bus
  { id: "sens_ph_bus", label: "4-Ch pH Bus Array", type: "sensor", domain: "smart_water", field: "ph1", x: 340, y: 490, r: 15, uri: "http://enviromap-kg/sensor/SmartWaterPHBus" },
  { id: "sens_tds_bus", label: "4-Ch TDS Bus Array", type: "sensor", domain: "smart_water", field: "tds1", x: 580, y: 490, r: 15, uri: "http://enviromap-kg/sensor/SmartWaterTDSBus" },

  // Observable Properties (SAREF / SOSA)
  { id: "prop_wtemp", label: "WaterTemperature", type: "property", domain: "hydroponics", x: 260, y: 220, r: 15, uri: "https://saref.etsi.org/saref4watr/WaterTemperature" },
  { id: "prop_turb", label: "Turbidity", type: "property", domain: "hydroponics", x: 250, y: 280, r: 15, uri: "https://saref.etsi.org/saref4watr/Turbidity" },
  { id: "prop_tds", label: "TotalDissolvedSolids", type: "property", domain: "cross_domain", x: 360, y: 370, r: 16, uri: "https://saref.etsi.org/saref4watr/TotalDissolvedSolids" },
  { id: "prop_ph", label: "HydrogenIonConcentration", type: "property", domain: "cross_domain", x: 340, y: 290, r: 16, uri: "https://saref.etsi.org/saref4watr/HydrogenIonConcentration" },
  { id: "prop_temp", label: "Temperature (Core)", type: "property", domain: "cross_domain", x: 460, y: 130, r: 16, uri: "https://saref.etsi.org/core/Temperature" },
  { id: "prop_hum", label: "Humidity (Core)", type: "property", domain: "cross_domain", x: 540, y: 80, r: 15, uri: "https://saref.etsi.org/core/Humidity" },
  { id: "prop_aqi", label: "AirQualityIndex", type: "property", domain: "air_quality", x: 670, y: 220, r: 15, uri: "https://saref.etsi.org/saref4envi/AirQualityIndex" },
  { id: "prop_pm25", label: "CalibratedPM25", type: "property", domain: "air_quality", x: 680, y: 280, r: 15, uri: "https://saref.etsi.org/saref4envi/CalibratedPM25Concentration" },
  { id: "prop_pm10", label: "PM10Concentration", type: "property", domain: "air_quality", x: 740, y: 250, r: 14, uri: "https://saref.etsi.org/saref4envi/PM10Concentration" },
  { id: "prop_co2", label: "CO2Concentration", type: "property", domain: "air_quality", x: 610, y: 310, r: 14, uri: "https://saref.etsi.org/saref4envi/CO2Concentration" },
  { id: "prop_co", label: "CarbonMonoxide", type: "property", domain: "air_quality", x: 560, y: 350, r: 13, uri: "https://saref.etsi.org/saref4envi/CarbonMonoxide" },

  // Standard Units of Measure (QUDT)
  { id: "unit_c", label: "°C (Degree Celsius)", type: "unit", domain: "cross_domain", x: 380, y: 70, r: 12, uri: "http://qudt.org/vocab/unit/DEG_C" },
  { id: "unit_ppm", label: "PPM (Parts Per Million)", type: "unit", domain: "cross_domain", x: 470, y: 360, r: 12, uri: "http://qudt.org/vocab/unit/PPM" },
  { id: "unit_ntu", label: "NTU (Turbidity)", type: "unit", domain: "hydroponics", x: 190, y: 270, r: 12, uri: "http://qudt.org/vocab/unit/NTU" },
  { id: "unit_ph", label: "pH Scale", type: "unit", domain: "cross_domain", x: 260, y: 320, r: 12, uri: "http://qudt.org/vocab/unit/PH" },
  { id: "unit_aqi", label: "AQI Scale", type: "unit", domain: "air_quality", x: 740, y: 200, r: 12, uri: "http://qudt.org/vocab/unit/AQI" },
  { id: "unit_ugm3", label: "µg/m³ (Density)", type: "unit", domain: "air_quality", x: 760, y: 310, r: 12, uri: "http://qudt.org/vocab/unit/MicroGM-PER-M3" }
];

const INITIAL_EDGES = [
  // Core to Platforms
  { source: "core_kg", target: "plat_hydro", label: "enviromap:federatesDomain" },
  { source: "core_kg", target: "plat_air", label: "enviromap:federatesDomain" },
  { source: "core_kg", target: "plat_water", label: "enviromap:federatesDomain" },

  // Platforms to Sensors
  { source: "plat_hydro", target: "sens_wtemp", label: "sosa:hosts" },
  { source: "plat_hydro", target: "sens_turb", label: "sosa:hosts" },
  { source: "plat_hydro", target: "sens_tds", label: "sosa:hosts" },
  { source: "plat_hydro", target: "sens_ph", label: "sosa:hosts" },
  { source: "plat_hydro", target: "sens_dht_hydro", label: "sosa:hosts" },

  { source: "plat_air", target: "sens_pms", label: "sosa:hosts" },
  { source: "plat_air", target: "sens_mq135", label: "sosa:hosts" },
  { source: "plat_air", target: "sens_co2", label: "sosa:hosts" },
  { source: "plat_air", target: "sens_mq7", label: "sosa:hosts" },
  { source: "plat_air", target: "sens_mq4", label: "sosa:hosts" },
  { source: "plat_air", target: "sens_smoke", label: "sosa:hosts" },
  { source: "plat_air", target: "sens_nh4", label: "sosa:hosts" },

  { source: "plat_water", target: "sens_ph_bus", label: "sosa:hosts" },
  { source: "plat_water", target: "sens_tds_bus", label: "sosa:hosts" },

  // Sensors to Observable Properties
  { source: "sens_wtemp", target: "prop_wtemp", label: "sosa:observes" },
  { source: "sens_turb", target: "prop_turb", label: "sosa:observes" },
  { source: "sens_tds", target: "prop_tds", label: "sosa:observes" },
  { source: "sens_ph", target: "prop_ph", label: "sosa:observes" },
  { source: "sens_dht_hydro", target: "prop_temp", label: "sosa:observes" },
  { source: "sens_dht_hydro", target: "prop_hum", label: "sosa:observes" },

  { source: "sens_pms", target: "prop_pm25", label: "sosa:observes" },
  { source: "sens_pms", target: "prop_pm10", label: "sosa:observes" },
  { source: "sens_mq135", target: "prop_aqi", label: "sosa:observes" },
  { source: "sens_co2", target: "prop_co2", label: "sosa:observes" },
  { source: "sens_mq7", target: "prop_co", label: "sosa:observes" },

  { source: "sens_ph_bus", target: "prop_ph", label: "sosa:observes" },
  { source: "sens_tds_bus", target: "prop_tds", label: "sosa:observes" },

  // Features of Interest
  { source: "plat_hydro", target: "foi_hydro", label: "sosa:hasFeatureOfInterest" },
  { source: "plat_air", target: "foi_air", label: "sosa:hasFeatureOfInterest" },
  { source: "plat_water", target: "foi_water", label: "sosa:hasFeatureOfInterest" },

  // Properties to Units
  { source: "prop_temp", target: "unit_c", label: "saref:isMeasuredIn" },
  { source: "prop_wtemp", target: "unit_c", label: "saref:isMeasuredIn" },
  { source: "prop_tds", target: "unit_ppm", label: "saref:isMeasuredIn" },
  { source: "prop_turb", target: "unit_ntu", label: "saref:isMeasuredIn" },
  { source: "prop_ph", target: "unit_ph", label: "saref:isMeasuredIn" },
  { source: "prop_aqi", target: "unit_aqi", label: "saref:isMeasuredIn" },
  { source: "prop_pm25", target: "unit_ugm3", label: "saref:isMeasuredIn" },

  // Cross-Domain Bridges
  { source: "prop_wtemp", target: "prop_temp", label: "rdfs:subClassOf" },
  { source: "prop_tds", target: "core_kg", label: "enviromap:crossDomainBridge" },
  { source: "prop_ph", target: "core_kg", label: "enviromap:crossDomainBridge" }
];

const NODE_COLORS = {
  hub: { bg: "#8957e5", stroke: "#a371f7", text: "#ffffff", label: "Semantic Hub" },
  platform: { bg: "#1f6feb", stroke: "#388bfd", text: "#ffffff", label: "IoT Platform" },
  sensor: { bg: "#238636", stroke: "#3fb950", text: "#ffffff", label: "Physical Sensor" },
  property: { bg: "#d29922", stroke: "#e3b341", text: "#0d1117", label: "Observable Property" },
  foi: { bg: "#bf4b8a", stroke: "#db61a2", text: "#ffffff", label: "Feature of Interest" },
  unit: { bg: "#bd561d", stroke: "#f0883e", text: "#ffffff", label: "Unit of Measure" }
};

function InteractiveKGNetwork({ records = [] }) {
  const [nodes, setNodes] = useState(INITIAL_NODES);
  const [selectedNode, setSelectedNode] = useState(INITIAL_NODES[0]);
  const [filterDomain, setFilterDomain] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [draggingNode, setDraggingNode] = useState(null);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1.0);

  // Map latest live values into nodes
  const liveNodeMap = useMemo(() => {
    const valMap = {};
    records.forEach(r => {
      const k = `${r.domain}_${r.source_field}`;
      valMap[k] = r.value;
      valMap[r.source_field] = r.value;
    });
    return valMap;
  }, [records]);

  // Handle node drag
  const handleMouseDownNode = (e, n) => {
    e.stopPropagation();
    setDraggingNode(n.id);
    setSelectedNode(n);
  };

  const handleMouseDownCanvas = (e) => {
    setIsPanning(true);
    setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e) => {
    if (draggingNode) {
      const svg = e.currentTarget.getBoundingClientRect();
      const clientX = (e.clientX - svg.left - pan.x) / zoom;
      const clientY = (e.clientY - svg.top - pan.y) / zoom;
      setNodes(prev => prev.map(n => n.id === draggingNode ? { ...n, x: Math.max(30, Math.min(900, clientX)), y: Math.max(30, Math.min(570, clientY)) } : n));
    } else if (isPanning) {
      setPan({ x: e.clientX - panStart.x, y: e.clientY - panStart.y });
    }
  };

  const handleMouseUp = () => {
    setDraggingNode(null);
    setIsPanning(false);
  };

  // Filtered nodes and edges
  const filteredNodes = useMemo(() => {
    return nodes.filter(n => {
      if (filterDomain !== "all" && n.domain !== filterDomain && n.domain !== "cross_domain") {
        return false;
      }
      if (searchTerm && !n.label.toLowerCase().includes(searchTerm.toLowerCase()) && !n.type.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }
      return true;
    });
  }, [nodes, filterDomain, searchTerm]);

  const filteredNodeIds = useMemo(() => new Set(filteredNodes.map(n => n.id)), [filteredNodes]);

  const filteredEdges = useMemo(() => {
    return INITIAL_EDGES.filter(e => filteredNodeIds.has(e.source) && filteredNodeIds.has(e.target));
  }, [filteredNodeIds]);

  const nodePosMap = useMemo(() => {
    const map = {};
    nodes.forEach(n => { map[n.id] = n; });
    return map;
  }, [nodes]);

  // Selected node relationships
  const selectedRelations = useMemo(() => {
    if (!selectedNode) return { incoming: [], outgoing: [] };
    const outgoing = INITIAL_EDGES.filter(e => e.source === selectedNode.id).map(e => ({
      rel: e.label,
      target: nodePosMap[e.target]
    }));
    const incoming = INITIAL_EDGES.filter(e => e.target === selectedNode.id).map(e => ({
      rel: e.label,
      source: nodePosMap[e.source]
    }));
    return { incoming, outgoing };
  }, [selectedNode, nodePosMap]);

  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm space-y-4">
      {/* 1. Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-[#21262d] pb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#1f6feb] animate-pulse"></span>
            <h3 className="text-sm font-bold text-white tracking-wide uppercase">
              Interactive Knowledge Graph Network (W3C SOSA / SAREF Ontology Topology)
            </h3>
          </div>
          <p className="text-[11px] text-[#8b949e] mt-0.5">
            LOD-style visual network of entities and semantic relationships across Hydroponics, Air Quality, and Smart Water Bus.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Search entity..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-[#0d1117] border border-[#30363d] rounded px-2.5 py-1 text-xs text-white placeholder-[#8b949e] focus:outline-none focus:border-[#58a6ff] w-36"
          />
          <div className="flex rounded border border-[#30363d] overflow-hidden text-xs">
            <button onClick={() => setZoom(z => Math.min(2.0, z + 0.15))} className="px-2 py-1 bg-[#21262d] hover:bg-[#30363d] text-white">+</button>
            <button onClick={() => setZoom(z => Math.max(0.5, z - 0.15))} className="px-2 py-1 bg-[#21262d] hover:bg-[#30363d] text-white">-</button>
            <button onClick={() => { setZoom(1.0); setPan({ x: 0, y: 0 }); }} className="px-2 py-1 bg-[#21262d] hover:bg-[#30363d] text-[#8b949e] text-[10px]">Reset</button>
          </div>
        </div>
      </div>

      {/* 2. Cluster Filter Buttons & Category Legend */}
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex flex-wrap gap-1.5">
          <button
            onClick={() => setFilterDomain("all")}
            className={`px-2.5 py-1 rounded text-[11px] font-mono font-semibold transition-colors ${filterDomain === "all" ? "bg-[#1f6feb] text-white" : "bg-[#21262d] text-[#8b949e] hover:text-white"}`}
          >
            All Subsystems ({nodes.length} Nodes)
          </button>
          <button
            onClick={() => setFilterDomain("hydroponics")}
            className={`px-2.5 py-1 rounded text-[11px] font-mono font-semibold transition-colors ${filterDomain === "hydroponics" ? "bg-[#238636] text-white" : "bg-[#21262d] text-[#8b949e] hover:text-white"}`}
          >
            Hydroponics Cluster
          </button>
          <button
            onClick={() => setFilterDomain("air_quality")}
            className={`px-2.5 py-1 rounded text-[11px] font-mono font-semibold transition-colors ${filterDomain === "air_quality" ? "bg-[#1f6feb] text-white" : "bg-[#21262d] text-[#8b949e] hover:text-white"}`}
          >
            Air Quality Cluster
          </button>
          <button
            onClick={() => setFilterDomain("smart_water")}
            className={`px-2.5 py-1 rounded text-[11px] font-mono font-semibold transition-colors ${filterDomain === "smart_water" ? "bg-[#38bdf8] text-[#0d1117]" : "bg-[#21262d] text-[#8b949e] hover:text-white"}`}
          >
            Smart Water Bus Cluster
          </button>
          <button
            onClick={() => setFilterDomain("cross_domain")}
            className={`px-2.5 py-1 rounded text-[11px] font-mono font-semibold transition-colors ${filterDomain === "cross_domain" ? "bg-[#8957e5] text-white" : "bg-[#21262d] text-[#8b949e] hover:text-white"}`}
          >
            Cross-Domain Bridges
          </button>
        </div>

        {/* LOD Color Legend */}
        <div className="flex flex-wrap items-center gap-3 text-[10px] text-[#8b949e] font-mono">
          {Object.entries(NODE_COLORS).map(([type, cfg]) => (
            <div key={type} className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: cfg.bg, border: `1px solid ${cfg.stroke}` }}></span>
              <span>{cfg.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 3. Interactive Canvas + Entity Inspector Sidecard */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* SVG Network Canvas */}
        <div
          className="lg:col-span-3 bg-[#0d1117] border border-[#21262d] rounded-lg overflow-hidden relative cursor-grab active:cursor-grabbing"
          style={{ height: "540px" }}
          onMouseDown={handleMouseDownCanvas}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          <svg className="w-full h-full select-none" viewBox="0 0 940 600">
            <defs>
              <marker id="arrow" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#30363d" />
              </marker>
              <marker id="arrow-selected" viewBox="0 0 10 10" refX="20" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#58a6ff" />
              </marker>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
              {/* Relationship Edges */}
              {filteredEdges.map((e, idx) => {
                const s = nodePosMap[e.source];
                const t = nodePosMap[e.target];
                if (!s || !t) return null;

                const isConnected = selectedNode && (selectedNode.id === e.source || selectedNode.id === e.target);
                const strokeColor = isConnected ? "#58a6ff" : "#21262d";
                const strokeWidth = isConnected ? 2.2 : 1.2;
                const marker = isConnected ? "url(#arrow-selected)" : "url(#arrow)";

                const midX = (s.x + t.x) / 2;
                const midY = (s.y + t.y) / 2;

                return (
                  <g key={`edge-${idx}`}>
                    <line
                      x1={s.x}
                      y1={s.y}
                      x2={t.x}
                      y2={t.y}
                      stroke={strokeColor}
                      strokeWidth={strokeWidth}
                      strokeDasharray={e.label.includes("subClass") || e.label.includes("Bridge") ? "4 4" : "none"}
                      markerEnd={marker}
                    />
                    {isConnected && (
                      <text x={midX} y={midY - 4} fill="#8b949e" fontSize={8} fontFamily="monospace" textAnchor="middle" className="pointer-events-none select-none">
                        {e.label.split(":")[1] || e.label}
                      </text>
                    )}
                  </g>
                );
              })}

              {/* Entity Nodes */}
              {filteredNodes.map((n) => {
                const isSelected = selectedNode && selectedNode.id === n.id;
                const isConnected = selectedNode && (
                  selectedNode.id === n.id ||
                  INITIAL_EDGES.some(e => (e.source === selectedNode.id && e.target === n.id) || (e.target === selectedNode.id && e.source === n.id))
                );
                const cfg = NODE_COLORS[n.type] || NODE_COLORS.property;
                const liveVal = n.field ? liveNodeMap[n.field] : null;

                return (
                  <g
                    key={n.id}
                    transform={`translate(${n.x}, ${n.y})`}
                    onMouseDown={(e) => handleMouseDownNode(e, n)}
                    className="cursor-pointer transition-transform"
                    style={{ filter: isSelected ? "url(#glow)" : "none" }}
                  >
                    {/* Pulsing Aura for Selected or Live Sensor */}
                    {isSelected && (
                      <circle r={n.r + 7} fill="none" stroke="#58a6ff" strokeWidth={2} strokeDasharray="3 3" className="animate-spin" />
                    )}

                    {/* Node Body */}
                    <circle
                      r={n.r}
                      fill={cfg.bg}
                      stroke={isSelected ? "#ffffff" : cfg.stroke}
                      strokeWidth={isSelected ? 3 : 1.8}
                      opacity={selectedNode && !isConnected ? 0.35 : 1}
                    />

                    {/* Node Icon or Label abbreviation */}
                    <text
                      textAnchor="middle"
                      dy="4"
                      fill={cfg.text}
                      fontSize={n.r > 16 ? 9 : 8}
                      fontWeight="bold"
                      fontFamily="monospace"
                      className="pointer-events-none select-none"
                    >
                      {n.type === "hub" ? "KG" : n.type === "platform" ? "IOT" : n.type === "sensor" ? "SEN" : n.type === "unit" ? "UNIT" : "PROP"}
                    </text>

                    {/* Node Text Label Below */}
                    <text
                      textAnchor="middle"
                      y={n.r + 12}
                      fill={isSelected ? "#58a6ff" : (selectedNode && !isConnected ? "#484f58" : "#c9d1d9")}
                      fontSize={9}
                      fontFamily="monospace"
                      fontWeight={isSelected ? "bold" : "normal"}
                      className="pointer-events-none select-none"
                    >
                      {n.label}
                    </text>

                    {/* Live Sensor Badge on Node if available */}
                    {liveVal !== undefined && liveVal !== null && (
                      <g transform={`translate(${n.r - 2}, ${-n.r + 2})`}>
                        <rect x={-4} y={-8} width={28} height={12} rx={4} fill="#0d1117" stroke="#238636" strokeWidth={1} />
                        <text x={10} y={1} fill="#3fb950" fontSize={7} fontWeight="bold" fontFamily="monospace" textAnchor="middle">
                          {liveVal < 0 ? "-1.0" : typeof liveVal === "number" ? liveVal.toFixed(1) : liveVal}
                        </text>
                      </g>
                    )}
                  </g>
                );
              })}
            </g>
          </svg>

          {/* Interactive Hint */}
          <div className="absolute bottom-2 left-2 text-[10px] text-[#8b949e] font-mono bg-[#161b22]/90 px-2 py-1 rounded border border-[#21262d] pointer-events-none">
            Click node to inspect | Drag node to reposition | Drag canvas to pan
          </div>
        </div>

        {/* 4. Entity Inspector Sidecard */}
        <div className="bg-[#0d1117] border border-[#21262d] rounded-lg p-3 flex flex-col justify-between text-xs space-y-3">
          {selectedNode ? (
            <div className="space-y-3">
              <div className="border-b border-[#21262d] pb-2">
                <span className="text-[10px] font-mono uppercase text-[#8b949e] block">Entity Inspector</span>
                <h4 className="text-sm font-bold text-white tracking-tight mt-0.5">{selectedNode.label}</h4>
                <div className="flex items-center gap-1.5 mt-1.5">
                  <span
                    className="px-2 py-0.5 rounded text-[10px] font-mono font-bold"
                    style={{ backgroundColor: `${NODE_COLORS[selectedNode.type]?.bg}33`, color: NODE_COLORS[selectedNode.type]?.stroke }}
                  >
                    {NODE_COLORS[selectedNode.type]?.label || selectedNode.type}
                  </span>
                  <span className="px-1.5 py-0.5 rounded bg-[#21262d] text-[#8b949e] text-[10px] font-mono">
                    {selectedNode.domain}
                  </span>
                </div>
              </div>

              {/* W3C URI */}
              <div>
                <span className="text-[10px] text-[#8b949e] block uppercase font-mono">W3C Concept URI</span>
                <code className="text-[10px] text-[#58a6ff] break-all block bg-[#161b22] p-1.5 rounded mt-0.5 border border-[#21262d]">
                  {selectedNode.uri || `http://enviromap-kg.ontology/${selectedNode.id}`}
                </code>
              </div>

              {/* Live Sensor Telemetry (if sensor or property) */}
              {selectedNode.field && liveNodeMap[selectedNode.field] !== undefined && (
                <div className="bg-[#161b22] border border-[#238636]/40 rounded p-2 text-xs">
                  <span className="text-[10px] text-[#8b949e] uppercase block font-mono">Real-Time Stream Value</span>
                  <div className="text-lg font-bold font-mono text-white mt-0.5">
                    {liveNodeMap[selectedNode.field] < 0 ? (
                      <span className="text-[#f85149]">-1.0 (Hardware Error)</span>
                    ) : (
                      <span>{liveNodeMap[selectedNode.field]}</span>
                    )}
                  </div>
                  <span className="text-[9px] text-[#3fb950] font-mono block mt-0.5">STREAMING FROM POSTGRESQL</span>
                </div>
              )}

              {/* Semantic Relationships */}
              <div>
                <span className="text-[10px] text-[#8b949e] block uppercase font-mono mb-1">
                  Connected Relationships ({selectedRelations.outgoing.length + selectedRelations.incoming.length})
                </span>

                <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                  {selectedRelations.outgoing.map((r, i) => (
                    <div
                      key={`out-${i}`}
                      onClick={() => r.target && setSelectedNode(r.target)}
                      className="p-1.5 rounded bg-[#161b22] border border-[#21262d] hover:border-[#58a6ff] cursor-pointer text-[10px] font-mono flex items-center justify-between"
                    >
                      <span className="text-[#d29922]">{r.rel.split(":")[1] || r.rel} &rarr;</span>
                      <span className="text-white truncate max-w-[120px]">{r.target?.label}</span>
                    </div>
                  ))}

                  {selectedRelations.incoming.map((r, i) => (
                    <div
                      key={`in-${i}`}
                      onClick={() => r.source && setSelectedNode(r.source)}
                      className="p-1.5 rounded bg-[#161b22] border border-[#21262d] hover:border-[#58a6ff] cursor-pointer text-[10px] font-mono flex items-center justify-between"
                    >
                      <span className="text-[#58a6ff]">&larr; {r.rel.split(":")[1] || r.rel}</span>
                      <span className="text-white truncate max-w-[120px]">{r.source?.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-[#8b949e]">
              <p>Click on any node in the graph to inspect its semantic relationships.</p>
            </div>
          )}

          <div className="border-t border-[#21262d] pt-2 text-[10px] text-[#8b949e] font-mono flex justify-between">
            <span>Graph Triples: 1,045,274</span>
            <span className="text-[#3fb950]">W3C RDF/OWL</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Tab: Knowledge Graph Topology (Interactive Network Graph + Static Bar Charts)
// -----------------------------------------------------------------------------
function TabAnalytics({ records }) {
  const conceptCounts = useMemo(() => {
    const map = {};
    records.forEach(r => {
      if (!map[r.concept]) map[r.concept] = { concept: r.concept, count: 0 };
      map[r.concept].count += 1;
    });
    return Object.values(map).sort((a, b) => b.count - a.count).slice(0, 12);
  }, [records]);

  const domainDistribution = useMemo(() => {
    const map = {};
    records.forEach(r => {
      map[r.domain] = (map[r.domain] || 0) + 1;
    });
    return Object.entries(map).map(([domain, count]) => ({ domain, count }));
  }, [records]);

  return (
    <div className="space-y-6">
      {/* 1. Interactive LOD-Style Visual Knowledge Graph Network */}
      <InteractiveKGNetwork records={records} />

      {/* 2. Static Analytics & Distribution Bar Charts (PRESERVED 100% INTACT) */}
      <div className="text-xs font-semibold text-[#58a6ff] uppercase tracking-wider border-b border-[#21262d] pb-2 pt-2 flex justify-between items-center">
        <span>KNOWLEDGE GRAPH STATISTICAL TOPOLOGY &amp; DISTRIBUTION</span>
        <span className="text-[#8b949e] font-mono text-[10px]">Harmonized RDF Observation Metrics</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
          <div className="text-xs font-semibold text-[#f0f6fc] mb-3">Top Observations per Semantic Class</div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={conceptCounts} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                <XAxis type="number" stroke="#8b949e" tick={{ fontSize: 10 }} />
                <YAxis dataKey="concept" type="category" stroke="#8b949e" tick={{ fontSize: 9 }} width={140} />
                <Tooltip contentStyle={{ backgroundColor: "#161b22", borderColor: "#30363d", color: "#f0f6fc", fontSize: "11px" }} />
                <Bar dataKey="count" name="Observations" fill="#1f6feb" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
          <div className="text-xs font-semibold text-[#f0f6fc] mb-3">Observations by Autonomous Environment</div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={domainDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                <XAxis dataKey="domain" stroke="#8b949e" tick={{ fontSize: 10 }} />
                <YAxis stroke="#8b949e" tick={{ fontSize: 10 }} />
                <Tooltip contentStyle={{ backgroundColor: "#161b22", borderColor: "#30363d", color: "#f0f6fc", fontSize: "11px" }} />
                <Bar dataKey="count" name="Streamed Points" fill="#3fb950" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Tab: Graph-RAG Natural Language to SPARQL Explorer
// -----------------------------------------------------------------------------
function GraphRAGTab() {
  const [question, setQuestion] = useState("What are the latest observations recorded across domains?");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [showSparql, setShowSparql] = useState(true);

  const presets = [
    "What are the latest observations recorded across domains?",
    "List all deployed W3C SOSA Sensors and host Platforms",
    "What is the highest temperature recorded in hydroponics?",
    "Compare pH and TDS readings on Smart Water Bus wq_bus_sensor",
    "Identify offline sensors with hardware fault codes (-1.0)",
    "Find all observations exceeding threshold 100"
  ];

  const runQuery = async (qText) => {
    const q = qText || question;
    if (!q) return;
    setLoading(true);
    try {
      const res = await fetch("/api/query-rag", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q })
      });
      const data = await res.json();
      setResponse(data);
    } catch (e) {
      setResponse({
        status: "error",
        summary: "Error communicating with Graph-RAG service.",
        results: []
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-xs font-semibold text-[#58a6ff] uppercase tracking-wider border-b border-[#21262d] pb-2">
        GRAPH-RAG &amp; SPARQL KNOWLEDGE DISCOVERY
      </div>

      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
        <label className="block text-xs font-semibold text-[#8b949e] uppercase tracking-wider mb-2">
          Natural Language Semantic Query
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && runQuery()}
            placeholder="Ask a question about environmental sensors, W3C SOSA observations, or thresholds..."
            className="flex-1 bg-[#0d1117] border border-[#30363d] rounded px-3 py-2 text-xs text-white focus:outline-none focus:border-[#58a6ff]"
          />
          <button
            onClick={() => runQuery()}
            disabled={loading}
            className="px-4 py-2 bg-[#1f6feb] hover:bg-[#388bfd] text-white text-xs font-semibold rounded transition-colors disabled:opacity-50"
          >
            {loading ? "Reasoning..." : "Execute Query"}
          </button>
        </div>

        <div className="mt-3 flex flex-wrap gap-1.5 items-center">
          <span className="text-[10px] text-[#8b949e] uppercase font-semibold mr-1">Presets:</span>
          {presets.map((p, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuestion(p);
                runQuery(p);
              }}
              className="text-[10px] px-2 py-0.5 rounded bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] transition-colors border border-[#30363d]"
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {response && (
        <div className="space-y-4">
          <div className="bg-[#161b22] border border-[#238636]/40 rounded-lg p-4 shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-semibold text-[#3fb950] uppercase tracking-wider">Semantic Synthesis Answer</span>
              <button onClick={() => setShowSparql(!showSparql)} className="text-[10px] text-[#58a6ff] hover:underline font-mono">
                {showSparql ? "Hide SPARQL" : "View SPARQL"}
              </button>
            </div>
            <p className="text-xs text-[#c9d1d9] leading-relaxed">{response.summary}</p>
          </div>

          {showSparql && response.sparql_query && (
            <div className="bg-[#0d1117] border border-[#30363d] rounded-lg p-3">
              <span className="text-[10px] text-[#8b949e] font-mono uppercase block mb-1">Generated W3C SPARQL 1.1 Query</span>
              <pre className="text-[11px] font-mono text-[#58a6ff] overflow-x-auto whitespace-pre">{response.sparql_query}</pre>
            </div>
          )}

          {response.results && response.results.length > 0 && (
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
              <span className="text-xs font-semibold text-white uppercase tracking-wider block mb-3">Knowledge Graph Matches ({response.results.length})</span>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-[#c9d1d9]">
                  <thead className="bg-[#0d1117] text-[#8b949e] text-[10px] uppercase font-mono border-b border-[#21262d]">
                    <tr>
                      <th className="py-2 px-3">Domain</th>
                      <th className="py-2 px-3">Physical Field</th>
                      <th className="py-2 px-3">Semantic Property</th>
                      <th className="py-2 px-3">Value</th>
                      <th className="py-2 px-3">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#21262d] font-mono text-[11px]">
                    {response.results.map((r, i) => (
                      <tr key={i} className="hover:bg-[#21262d]/50">
                        <td className="py-1.5 px-3">{r.domain}</td>
                        <td className="py-1.5 px-3 text-white"><code>{r.field}</code></td>
                        <td className="py-1.5 px-3 text-[#58a6ff]">{r.property}</td>
                        <td className="py-1.5 px-3 font-bold text-[#d29922]">{r.value}</td>
                        <td className="py-1.5 px-3 text-[#8b949e]">{r.time}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// -----------------------------------------------------------------------------
// Primary App Container with Dynamic Navigation & Auto-Refresh
// -----------------------------------------------------------------------------
export default function App() {
  const [kgData, setKgData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState("Last 7 Days");
  const [activeTab, setActiveTab] = useState("cross_domain");
  const [remainingSec, setRemainingSec] = useState(15);

  const fetchKG = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/kg-data?time_range=${encodeURIComponent(timeRange)}`);
      const data = await res.json();
      setKgData(data);
    } catch (e) {
      console.error("API error:", e);
    } finally {
      setLoading(false);
      setRemainingSec(15);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchKG();
  }, [fetchKG]);

  useEffect(() => {
    const timer = setInterval(() => {
      setRemainingSec((prev) => {
        if (prev <= 1) {
          fetchKG();
          return 15;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [fetchKG]);

  const records = kgData?.records || [];
  const units = kgData?.units || {};

  // Dynamically compute all distinct active domains discovered in PostgreSQL
  const availableTabs = useMemo(() => {
    const domainSet = new Set(records.map(r => r.domain));
    const list = [
      { id: "cross_domain", label: "Cross-Domain Timeline" }
    ];

    if (domainSet.has("hydroponics")) {
      list.push({ id: "hydroponics", label: "Hydroponics Ecosystem" });
    }
    if (domainSet.has("air_quality")) {
      list.push({ id: "air_quality", label: "Air Quality & Gases" });
    }
    if (domainSet.has("smart_water")) {
      list.push({ id: "smart_water", label: "Smart Water Bus (wq_bus)" });
    }

    // Automatically add tabs for any newly created/discovered domain!
    domainSet.forEach(d => {
      if (!["hydroponics", "air_quality", "smart_water"].includes(d)) {
        const title = d.replace(/_/g, " ").replace(/\\b\\w/g, c => c.toUpperCase());
        list.push({ id: d, label: `${title} Ecosystem` });
      }
    });

    list.push({ id: "topology", label: "Knowledge Graph Topology" });
    list.push({ id: "rag", label: "Graph-RAG Explorer", badge: "AI" });

    return list;
  }, [records]);

  return (
    <div className="flex min-h-screen bg-[#0d1117] text-[#c9d1d9]">
      {/* Sidebar */}
      <aside className="w-64 bg-[#161b22] border-r border-[#30363d] p-4 flex flex-col justify-between hidden md:flex">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-6 h-6 rounded bg-[#1f6feb] flex items-center justify-center font-bold text-white text-xs">EM</div>
            <span className="font-bold text-sm text-white tracking-tight">EnviroMap-KG</span>
          </div>
          <div className="text-[10px] text-[#8b949e] mb-4">
            Autonomous Multi-Domain Semantic Knowledge Graph
          </div>

          <div className="mb-4">
            <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-[#238636]/15 border border-[#238636]/40 text-[#3fb950] text-[11px] font-semibold w-fit">
              <span className="h-2 w-2 rounded-full bg-[#3fb950] animate-pulse"></span>
              LIVE STREAM ACTIVE ({kgData?.pipeline_age_min || 0}m ago)
            </div>
            <div className="text-[10px] text-[#8b949e] mt-1 font-mono">
              Auto-refresh in {remainingSec}s
            </div>
          </div>

          <hr className="border-[#21262d] my-4" />

          <div className="mb-5">
            <label className="block text-xs font-semibold text-[#8b949e] uppercase tracking-wider mb-2">
              DATA FILTER
            </label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="w-full bg-[#0d1117] border border-[#30363d] rounded px-3 py-1.5 text-xs text-white focus:outline-none focus:border-[#58a6ff]"
            >
              <option value="Last 7 Days">Last 7 Days</option>
              <option value="Last 3 Days">Last 3 Days</option>
              <option value="Last 24 Hours">Last 24 Hours</option>
              <option value="All Records">All Records</option>
            </select>
            <div className="text-[10px] text-[#8b949e] mt-1.5">
              Active window: <span className="text-[#38bdf8] font-mono">{timeRange}</span>
            </div>
          </div>

          <hr className="border-[#21262d] my-4" />

          <div>
            <div className="text-[11px] font-semibold text-[#8b949e] uppercase tracking-wider mb-2">
              W3C STANDARDS ALIGNMENT
            </div>
            <ul className="text-[11px] text-[#8b949e] space-y-1.5">
              <li>- <strong className="text-[#c9d1d9]">SAREF Core</strong> (ETSI TS 103 264)</li>
              <li>- <strong className="text-[#c9d1d9]">SAREF4WATR &amp; 4ENVI</strong></li>
              <li>- <strong className="text-[#c9d1d9]">W3C SSN / SOSA</strong></li>
              <li>- <strong className="text-[#c9d1d9]">oneM2M / ThingsBoard</strong></li>
            </ul>
          </div>
        </div>

        <button
          onClick={fetchKG}
          disabled={loading}
          className="w-full py-2 px-3 rounded bg-[#21262d] hover:bg-[#30363d] border border-[#30363d] text-xs font-semibold text-[#c9d1d9] transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {loading ? "Updating..." : "Manual Cache Refresh"}
        </button>
      </aside>

      {/* Main Area */}
      <main className="flex-1 p-6 overflow-y-auto">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">Autonomous Semantic Knowledge Graph Monitoring</h1>
            <p className="text-xs text-[#8b949e]">Auto-discovering live PostgreSQL environmental subsystems</p>
          </div>
          <div className="text-right">
            <div className="text-[10px] text-[#8b949e]">Repository Updated</div>
            <div className="text-xs font-bold text-white font-mono">{kgData?.last_modified || "2026-09-22 17:25:00"}</div>
          </div>
        </div>

        <TopKPIs
          totalTriples={kgData?.total_triples || 1045274}
          totalObservations={kgData?.total_observations || 12627}
          records={records}
          domainObservations={kgData?.domain_observations || {}}
        />

        <hr className="border-[#21262d] my-4" />

        {/* Dynamic Navigation Bar */}
        <div className="mb-6 border-b border-[#30363d]">
          <nav className="flex flex-wrap gap-2 bg-[#161b22] p-1.5 rounded-lg border border-[#30363d] w-fit">
            {availableTabs.map((tab) => {
              const active = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-md transition-all ${
                    active
                      ? "bg-[#21262d] text-white border border-[#30363d] shadow-sm font-bold"
                      : "text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#21262d]/50"
                  }`}
                >
                  <span>{tab.label}</span>
                  {tab.badge && (
                    <span className="px-1.5 py-0.2 rounded-full bg-[#1f6feb]/30 text-[#58a6ff] text-[9px] font-mono border border-[#1f6feb]/50">
                      {tab.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Dynamic Tab Renderers */}
        <div className="mt-2">
          {activeTab === "cross_domain" && (
            <TabCrossDomain records={records} units={units} timeRange={timeRange} totalObservations={kgData?.total_observations || 12627} />
          )}
          {activeTab === "hydroponics" && (
            <TabHydroponics records={records} units={units} timeRange={timeRange} />
          )}
          {activeTab === "air_quality" && (
            <TabAirQuality records={records} units={units} timeRange={timeRange} />
          )}
          {activeTab === "smart_water" && (
            <TabSmartWaterBus records={records} units={units} timeRange={timeRange} />
          )}
          {!["cross_domain", "hydroponics", "air_quality", "smart_water", "topology", "rag"].includes(activeTab) && (
            <TabDynamicDomain domain={activeTab} records={records} units={units} timeRange={timeRange} />
          )}
          {activeTab === "topology" && (
            <TabAnalytics records={records} />
          )}
          {activeTab === "rag" && (
            <GraphRAGTab />
          )}
        </div>
      </main>
    </div>
  );
}
'''

with open(r'C:\Users\Shreenithi\.gemini\antigravity\scratch\full_app.jsx', 'w', encoding='utf-8') as f:
    f.write(app_code)

with open(r'C:\Users\Shreenithi\.gemini\antigravity\scratch\react-dashboard\src\App.jsx', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("Generated full_app.jsx and updated react-dashboard/src/App.jsx successfully!")

