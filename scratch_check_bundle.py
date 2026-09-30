import urllib.request
import re

with urllib.request.urlopen('http://192.168.0.21/semantic-react/', timeout=5) as r:
    html = r.read().decode('utf-8')
print('HTML:', html)

match = re.search(r'src=["\']([^"\']+\.js)["\']', html)
if match:
    js_path = match.group(1).lstrip('./')
    full_url = f'http://192.168.0.21/semantic-react/{js_path}'
    print('Fetching bundle:', full_url)
    with urllib.request.urlopen(full_url, timeout=5) as r:
        js = r.read().decode('utf-8', errors='ignore')
    print('Bundle size:', len(js))
    print('Hardware Disconnect in bundle:', 'Hardware Disconnect' in js)
    print('22.99 in bundle:', '22.99' in js)
    print('8.82 in bundle:', '8.82' in js)
    print('653.14 in bundle:', '653.14' in js)
    print('kg-data in bundle:', 'kg-data' in js)
    for kw in ['math.sin', '22.48', 'points']:
        print(f'{kw} in bundle:', kw in js.lower())

