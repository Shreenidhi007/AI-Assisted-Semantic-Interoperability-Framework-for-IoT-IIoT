import urllib.request
import re

url = 'http://192.168.0.21/semantic-react/assets/index-c065a0c2.js'
with urllib.request.urlopen(url, timeout=5) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

matches = set(re.findall(r'["\'](/api/[^"\']+|http://[^"\':]+:[0-9]+/[^"\']*)["\']', content))
print('API endpoints in React bundle:')
for m in matches:
    print(' -', m)

# Also search for 'kg-data' or 'fetch'
print('\nOccurrences of kg-data in bundle:')
for line in content.split(';'):
    if 'kg-data' in line:
        print(' -', line[:200])

