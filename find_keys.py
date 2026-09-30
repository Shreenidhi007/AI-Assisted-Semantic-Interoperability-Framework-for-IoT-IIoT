import urllib.request

url = 'http://192.168.0.21/semantic-react/assets/index-c065a0c2.js'
with urllib.request.urlopen(url, timeout=5) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

# Search for RDF TRIPLES
idx = content.find('RDF TRIPLES')
print('Context around RDF TRIPLES (200 chars before and after):')
print(content[max(0, idx-200):min(len(content), idx+200)])

# Also search where a(p) is stored, and how p is unpacked
fetch_idx = content.find('a(p)')
print('\nContext around a(p):')
print(content[max(0, fetch_idx-150):min(len(content), fetch_idx+400)])

