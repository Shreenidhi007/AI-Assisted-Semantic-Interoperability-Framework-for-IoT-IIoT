import re

code = '''
const API_BASE = window.location.origin.includes(":") ? `http://${window.location.hostname}:8001` : "/api";
fetch(`${API_BASE}/api/kg-data`);
'''

pat_8001 = re.compile(r'window\.location\.origin\.includes\([^\)]*\)\s*\?\s*[`\'\"][^`\'\"]*8001[^`\'\"]*[`\'\"]\s*:\s*[`\'\"][^`\'\"]*[`\'\"]')
print('Matches:', bool(pat_8001.search(code)))
res = pat_8001.sub('""', code)
print('Result:\n', res)

