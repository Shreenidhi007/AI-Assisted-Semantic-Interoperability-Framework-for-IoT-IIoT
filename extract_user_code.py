import urllib.request

url = 'http://192.168.0.21/semantic-react/assets/index-7e159cf8.js'
with urllib.request.urlopen(url, timeout=5) as resp:
    js = resp.read().decode('utf-8', errors='ignore')

# Extract TabCrossDomain, TabAirQuality, TabAnalytics
for name in ["TabCrossDomain", "TabAirQuality", "TabAnalytics", "TopKPI"]:
    # Find markers
    pass

# Print the last 8000 characters of the bundle (which contains the user components)
print(js[-8000:])

