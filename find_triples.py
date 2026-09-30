import urllib.request
import re

url = 'http://192.168.0.21/semantic-react/assets/index-c065a0c2.js'
with urllib.request.urlopen(url, timeout=5) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

matches = [m.start() for m in re.finditer(r'RDF TRIPLES', content)]
print(f'Matches for RDF TRIPLES: {len(matches)}')
for idx in matches:
    print('---')
    print(content[max(0, idx-150):min(len(content), idx+250)])

