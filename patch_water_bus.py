#!/usr/bin/env python3
with open('full_app.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

target = """      <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
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
      </div>"""

replacement = """      {/* Dynamically Discovered Active Water Channels (temp, water_level, flow, etc.) */}
      {(() => {
        const standardFields = ['ph1', 'ph2', 'ph3', 'ph4', 'tds1', 'tds2', 'tds3', 'tds4'];
        const otherActive = [...new Set(waterRecords.map(r => r.source_field))].filter(f =>
          !standardFields.includes(f) && waterRecords.some(r => r.source_field === f && r.value !== null && r.value !== undefined)
        );

        const unmeasuredList = ["temp1", "temp2", "temp3", "temp4", "water_level"].filter(f => !otherActive.includes(f));

        return (
          <>
            {otherActive.length > 0 && (
              <div className="space-y-4">
                <div className="text-xs font-semibold text-[#58a6ff] uppercase tracking-wider border-b border-[#21262d] pb-2 flex justify-between items-center">
                  <span>AUXILIARY SENSOR STREAMS ({otherActive.length} DYNAMIC CHANNELS ACTIVE)</span>
                  <span className="text-[#3fb950] font-mono text-[10px] font-bold">AUTONOMOUS DETECTION</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {otherActive.map(f => {
                    const match = waterRecords.filter(r => r.source_field === f);
                    const latest = match[match.length - 1];
                    const unit = units[f] || (f.includes('temp') ? '°C' : (f.includes('level') ? 'cm' : ''));
                    return (
                      <div key={f} className="bg-[#161b22] border border-[#238636]/60 rounded-lg p-4 shadow-sm">
                        <div className="flex justify-between items-center text-[#8b949e] text-xs">
                          <span className="font-semibold text-white uppercase">{f.replace(/_/g, ' ')}</span>
                          <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#238636]/20 text-[#3fb950] font-mono font-bold">ONLINE</span>
                        </div>
                        <div className="mt-2 text-2xl font-bold font-mono text-[#3fb950]">
                          {latest ? latest.value.toFixed(2) : '0.00'} <span className="text-xs text-[#8b949e]">{unit}</span>
                        </div>
                        <div className="mt-2 text-[10px] font-mono text-[#8b949e] border-t border-[#21262d] pt-1.5 flex justify-between">
                          <span>Field: <code>{f}</code></span>
                          <span className="text-[#58a6ff]">{latest?.concept || f}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {otherActive.map(f => {
                    const series = waterRecords.filter(r => r.source_field === f).map(r => ({
                      time: formatTime(r.time, timeRange),
                      value: r.value
                    }));
                    const unit = units[f] || (f.includes('temp') ? '°C' : (f.includes('level') ? 'cm' : ''));
                    return (
                      <div key={f} className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
                        <div className="text-xs font-semibold text-white mb-2 flex justify-between items-center">
                          <span>{f.toUpperCase().replace(/_/g, ' ')} TIMELINE</span>
                          <span className="text-xs font-mono text-[#3fb950]">Latest: {series.length ? series[series.length - 1].value : 'N/A'} {unit}</span>
                        </div>
                        <div className="h-56 w-full">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={series}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                              <XAxis dataKey="time" stroke="#8b949e" tick={{ fontSize: 10 }} />
                              <YAxis stroke="#8b949e" tick={{ fontSize: 10 }} unit={` ${unit}`} />
                              <Tooltip contentStyle={{ backgroundColor: "#161b22", borderColor: "#30363d", color: "#f0f6fc", fontSize: "11px" }} />
                              <Line type="monotone" dataKey="value" stroke="#3fb950" strokeWidth={2} dot={false} />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {unmeasuredList.length > 0 && (
              <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 shadow-sm">
                <div className="text-xs font-semibold text-[#8b949e] uppercase tracking-wider mb-3">
                  UNMEASURED BUS CHANNELS (NULL IN DATABASE)
                </div>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs font-mono">
                  {unmeasuredList.map(f => (
                    <div key={f} className="p-2.5 rounded bg-[#0d1117] border border-[#21262d]">
                      <span className="text-[#8b949e] text-[10px] block uppercase">{f}</span>
                      <span className="text-[#8b949e] font-bold">N/A</span>
                      <span className="text-[9px] text-[#8b949e] block mt-0.5">UNMEASURED (NULL)</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        );
      })()}"""

if target in text:
    text = text.replace(target, replacement)
    with open('full_app.jsx', 'w', encoding='utf-8') as f:
        f.write(text)
    print('[SUCCESS] Made TabSmartWaterBus fully dynamic!')
else:
    print('[WARNING] Target in TabSmartWaterBus not found verbatim')

