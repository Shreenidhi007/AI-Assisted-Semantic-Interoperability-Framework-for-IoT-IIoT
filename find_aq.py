import urllib.request
import re

url = 'http://192.168.0.21/semantic-react/assets/index-c065a0c2.js'
with urllib.request.urlopen(url, timeout=5) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

# Search for definition of aq
matches = re.findall(r'(\w+\s*=\s*(?:\([^\)]*\)|"[^"]*"|\'[^\']*\'))', content[content.find('/api/kg-data')-400:content.find('/api/kg-data')])
print('Definitions before /api/kg-data:')
for m in matches:
    print(' ', m)

