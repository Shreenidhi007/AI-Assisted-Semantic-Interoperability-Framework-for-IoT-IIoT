import urllib.request
import re

url = 'http://192.168.0.21/semantic-react/assets/index-c065a0c2.js'
with urllib.request.urlopen(url, timeout=5) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

# Search for where 'p=await' or state is set after fetch
fetch_idx = content.find('/api/kg-data')
print('Context around fetch /api/kg-data:')
print(content[max(0, fetch_idx-100):min(len(content), fetch_idx+300)])

# Search for RDF TRIPLES in the text
idx = content.find('RDF TRIPLES')
if idx != -1:
    print('\nContext around RDF TRIPLES:')
    print(content[max(0, idx-100):min(len(content), idx+200)])

idx_obs = content.find('OBSERVATIONS')
if idx_obs != -1:
    print('\nContext around OBSERVATIONS:')
    print(content[max(0, idx_obs-100):min(len(content), idx_obs+200)])

idx_hydro = content.find('No hydroponics records')
if idx_hydro != -1:
    print('\nContext around No hydroponics records:')
    print(content[max(0, idx_hydro-200):min(len(content), idx_hydro+200)])

