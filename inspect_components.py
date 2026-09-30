import urllib.request
import re

url = 'http://192.168.0.21/semantic-react/assets/index-7e159cf8.js'
with urllib.request.urlopen(url, timeout=5) as resp:
    js = resp.read().decode('utf-8', errors='ignore')

# Search for function declarations
# Look for "RDF TRIPLES"
idx_triples = js.find("RDF TRIPLES")
if idx_triples != -1:
    print("=== Found RDF TRIPLES at", idx_triples, "===")
    print(js[max(0, idx_triples-150):min(len(js), idx_triples+600)])

# Look for TabHydroponics function
idx_hydro = js.find("Hydroponic Sensor Network Metrics")
if idx_hydro != -1:
    print("\n=== Found Hydroponic Metrics at", idx_hydro, "===")
    # Search backwards for "function"
    fn_idx = js.rfind("function", 0, idx_hydro)
    print(js[fn_idx:idx_hydro+600])

