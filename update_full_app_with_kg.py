import os

# Complete script to generate the updated React App with the Interactive Knowledge Graph Network
# while preserving the static bar charts in TabAnalytics

kg_network_code = '''
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
'''

# Read current build_full_app.py
with open(r'C:\Users\Shreenithi\.gemini\antigravity\scratch\build_full_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace TabAnalytics definition in the app_code string
old_tab_analytics = """// -----------------------------------------------------------------------------
// Tab: Knowledge Graph Topology
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
      <div className="text-xs font-semibold text-[#58a6ff] uppercase tracking-wider border-b border-[#21262d] pb-2">
        KNOWLEDGE GRAPH TOPOLOGY &amp; DISTRIBUTION
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
}"""

new_tab_analytics = kg_network_code + """
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
}"""

if old_tab_analytics in content:
    content = content.replace(old_tab_analytics, new_tab_analytics)
    with open(r'C:\Users\Shreenithi\.gemini\antigravity\scratch\build_full_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully injected InteractiveKGNetwork into build_full_app.py!")
else:
    print("Could not find exact old_tab_analytics string. Checking lines...")

