import urllib.request
import re

url = 'http://192.168.0.21/semantic-react/assets/index-c065a0c2.js'
with urllib.request.urlopen(url, timeout=5) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

print('Bundle length:', len(content))

# Find the tab components definitions
tab_names = ["Cross-Domain Interoperability", "Hydroponics Domain", "Air Quality Domain", "Knowledge Graph Analytics"]
for name in tab_names:
    idx = content.find(name)
    print(f"\n=== Found '{name}' at index {idx} ===")
    print(content[max(0, idx-100):min(len(content), idx+250)])

# Find where the cross-domain line chart is rendered
idx_cross = content.find("SHARED CANONICAL CONCEPTS")
if idx_cross != -1:
    print("\n=== Context around SHARED CANONICAL CONCEPTS ===")
    print(content[idx_cross:idx_cross+1200])

# Find where the AQI gauge is rendered
idx_gauge = content.find("ATMOSPHERIC MONITORING METRICS")
if idx_gauge != -1:
    print("\n=== Context around ATMOSPHERIC MONITORING METRICS ===")
    print(content[idx_gauge:idx_gauge+1200])

