with open(r'C:\Users\Shreenithi\.gemini\antigravity\scratch\full_app.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace richCards and hydroFields in TabHydroponics
old_hydro_block = """  const richCards = [
    { title: "WATER TEMPERATURE", category: "WATER", field: "water_temperature", val: getLatestVal("water_temperature", "29.69"), minVal: getMinVal("water_temperature"), unit: "°C", optimal: "18-24°C", concept: "s4watr:WaterTemperature", color: "#38bdf8" },
    { title: "AMBIENT TEMPERATURE", category: "AMBIENT", field: "temperature", val: getLatestVal("temperature", "30.40"), minVal: getMinVal("temperature"), unit: "°C", optimal: "20-28°C", concept: "saref:Temperature", color: "#58a6ff" },
    { title: "RELATIVE HUMIDITY", category: "HUMIDITY", field: "humidity", val: getLatestVal("humidity", "77.9"), minVal: getMinVal("humidity"), unit: "%", optimal: "60-80%", concept: "saref:Humidity", color: "#3fb950" },
    { title: "PH VALUE", category: "CHEMISTRY", field: "ph", val: getLatestVal("ph", "2.84"), minVal: getMinVal("ph"), unit: "pH", optimal: "5.5-6.8", concept: "s4watr:HydrogenIonConcentration", color: "#a371f7" },
    { title: "TOTAL DISSOLVED SOLIDS", category: "SOLIDS", field: "tds", val: getLatestVal("tds", "14.51"), minVal: getMinVal("tds"), unit: "PPM", optimal: "500-800", concept: "s4watr:TotalDissolvedSolids", color: "#f0883e" },
    { title: "TURBIDITY", category: "OPTICAL", field: "turbidity", val: getLatestVal("turbidity", "2199.49"), minVal: getMinVal("turbidity"), unit: "NTU", optimal: "< 10 NTU", concept: "s4watr:Turbidity", color: "#e3b341" },
    { title: "ELECTRICAL CONDUCTIVITY", category: "CONDUCTIVITY", field: "ec", val: getLatestVal("ec", "29.02"), minVal: getMinVal("ec"), unit: "µS/cm", optimal: "20-40 µS/cm", concept: "s4watr:Conductivity", color: "#2ea043" },
    { title: "LIGHT LAYER 1", category: "PHOTONICS", field: "light_layer1", val: getLatestVal("light_layer1", "485.0"), minVal: getMinVal("light_layer1"), unit: "lux", optimal: "300-600 lux", concept: "saref:Light", color: "#e3b341" },
    { title: "LIGHT LAYER 2", category: "PHOTONICS", field: "light_layer2", val: getLatestVal("light_layer2", "420.0"), minVal: getMinVal("light_layer2"), unit: "lux", optimal: "300-600 lux", concept: "saref:Light", color: "#d29922" },
  ];

  const hydroFields = [
    "water_temperature",
    "turbidity",
    "tds",
    "temperature",
    "ambient_temperature",
    "humidity",
    "ph",
    "ec",
    "light_layer1",
    "light_layer2",
    "light_layer3"
  ];"""

new_hydro_block = """  // Only 6 physical sensors are installed and measured in PostgreSQL (onem2m_data)
  // light_layer1, light_layer2, light_layer3 are NULL in the database, and ec is not in the schema
  const richCards = [
    { title: "WATER TEMPERATURE", category: "WATER", field: "water_temperature", val: getLatestVal("water_temperature", "29.88"), minVal: getMinVal("water_temperature"), unit: "°C", optimal: "18-24°C", concept: "s4watr:WaterTemperature", color: "#38bdf8" },
    { title: "AMBIENT TEMPERATURE", category: "AMBIENT", field: "temperature", val: getLatestVal("temperature", "30.70"), minVal: getMinVal("temperature"), unit: "°C", optimal: "20-28°C", concept: "saref:Temperature", color: "#58a6ff" },
    { title: "RELATIVE HUMIDITY", category: "HUMIDITY", field: "humidity", val: getLatestVal("humidity", "77.60"), minVal: getMinVal("humidity"), unit: "%", optimal: "60-80%", concept: "saref:Humidity", color: "#3fb950" },
    { title: "PH VALUE", category: "CHEMISTRY", field: "ph", val: getLatestVal("ph", "2.83"), minVal: getMinVal("ph"), unit: "pH", optimal: "5.5-6.8", concept: "s4watr:HydrogenIonConcentration", color: "#a371f7" },
    { title: "TOTAL DISSOLVED SOLIDS", category: "SOLIDS", field: "tds", val: getLatestVal("tds", "13.77"), minVal: getMinVal("tds"), unit: "PPM", optimal: "500-800", concept: "s4watr:TotalDissolvedSolids", color: "#f0883e" },
    { title: "TURBIDITY", category: "OPTICAL", field: "turbidity", val: getLatestVal("turbidity", "2226.23"), minVal: getMinVal("turbidity"), unit: "NTU", optimal: "< 10 NTU", concept: "s4watr:Turbidity", color: "#e3b341" },
  ];

  // Only measured fields are charted (light layers and ec have 0 measurements in DB)
  const hydroFields = [
    "water_temperature",
    "turbidity",
    "tds",
    "temperature",
    "humidity",
    "ph"
  ];"""

if old_hydro_block in code:
    code = code.replace(old_hydro_block, new_hydro_block)
    print("Updated TabHydroponics cards successfully!")
else:
    print("Could not find old_hydro_block")

# Add the Unmeasured Hardware Diagnostics section at the end of TabHydroponics
unmeasured_section = """      {/* 3. Hardware Channel Inventory & Unmeasured Diagnostics */}
      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
        <div className="flex items-center justify-between border-b border-[#21262d] pb-2 mb-3">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#8b949e]"></span>
            <span className="text-xs font-semibold uppercase tracking-wider text-white">HARDWARE CHANNEL INVENTORY &amp; TELEMETRY STATUS</span>
          </div>
          <span className="text-[10px] font-mono text-[#8b949e]">Table: public.onem2m_data</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
          <div className="p-2.5 rounded bg-[#0d1117] border border-[#21262d]">
            <div className="flex justify-between items-center text-[10px] text-[#8b949e] uppercase">
              <span>light_layer1</span>
              <span className="px-1.5 py-0.2 rounded bg-[#21262d] text-[#8b949e] font-bold">UNMEASURED</span>
            </div>
            <div className="text-lg font-bold text-[#8b949e] mt-1">N/A <span className="text-[10px]">lux</span></div>
            <div className="text-[9px] text-[#8b949e] mt-1">NULL in PostgreSQL (0 readings)</div>
          </div>
          <div className="p-2.5 rounded bg-[#0d1117] border border-[#21262d]">
            <div className="flex justify-between items-center text-[10px] text-[#8b949e] uppercase">
              <span>light_layer2</span>
              <span className="px-1.5 py-0.2 rounded bg-[#21262d] text-[#8b949e] font-bold">UNMEASURED</span>
            </div>
            <div className="text-lg font-bold text-[#8b949e] mt-1">N/A <span className="text-[10px]">lux</span></div>
            <div className="text-[9px] text-[#8b949e] mt-1">NULL in PostgreSQL (0 readings)</div>
          </div>
          <div className="p-2.5 rounded bg-[#0d1117] border border-[#21262d]">
            <div className="flex justify-between items-center text-[10px] text-[#8b949e] uppercase">
              <span>light_layer3</span>
              <span className="px-1.5 py-0.2 rounded bg-[#21262d] text-[#8b949e] font-bold">UNMEASURED</span>
            </div>
            <div className="text-lg font-bold text-[#8b949e] mt-1">N/A <span className="text-[10px]">lux</span></div>
            <div className="text-[9px] text-[#8b949e] mt-1">NULL in PostgreSQL (0 readings)</div>
          </div>
          <div className="p-2.5 rounded bg-[#0d1117] border border-[#21262d]">
            <div className="flex justify-between items-center text-[10px] text-[#8b949e] uppercase">
              <span>ec</span>
              <span className="px-1.5 py-0.2 rounded bg-[#21262d] text-[#8b949e] font-bold">NO HARDWARE</span>
            </div>
            <div className="text-lg font-bold text-[#8b949e] mt-1">N/A <span className="text-[10px]">µS/cm</span></div>
            <div className="text-[9px] text-[#8b949e] mt-1">Not in database table columns</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Tab 3: Air Quality & Gas Sensors"""

target_end = """      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Tab 3: Air Quality & Gas Sensors"""

if target_end in code:
    code = code.replace(target_end, unmeasured_section)
    print("Added Unmeasured Hardware Diagnostics section successfully!")
else:
    print("Could not find target_end in code")

with open(r'C:\Users\Shreenithi\.gemini\antigravity\scratch\full_app.jsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved updated full_app.jsx!")

