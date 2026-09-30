import urllib.request
import time

url = 'http://192.168.0.21:8008/api/kg-data'
print('Sending GET to', url, 'with 90s timeout...')
t0 = time.time()
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=90) as resp:
        elapsed = time.time() - t0
        data = resp.read()
        print('SUCCESS in', round(elapsed, 2), 's! Status:', resp.getcode(), '| Bytes:', len(data))
        print('Preview:', data[:300].decode('utf-8', errors='ignore'))
except Exception as e:
    elapsed = time.time() - t0
    print('FAILED after', round(elapsed, 2), 's:', e)

