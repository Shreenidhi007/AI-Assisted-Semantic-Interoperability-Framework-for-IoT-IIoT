#!/usr/bin/env python3
"""
EnviroMap-KG: Complete One-Click API Backend Launcher & Health Verifier
Starts the multi-threaded Python REST API on Port 8008 so React gets live Knowledge Graph data.
"""

import os
import sys
import time
import subprocess
import urllib.request
import json

BASE_DIR = os.path.expanduser("~/semantic-interoperability-kg")
if not os.path.exists(BASE_DIR):
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

os.chdir(BASE_DIR)
print(f"Working Directory: {os.getcwd()}")

VENV_PYTHON = os.path.join(BASE_DIR, "venv", "bin", "python3")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

# 1. Download updated fixed_api_main.py to api/main.py
api_dir = os.path.join(BASE_DIR, "api")
os.makedirs(api_dir, exist_ok=True)
api_main_path = os.path.join(api_dir, "main.py")

print("1. Downloading high-speed zero-dependency API backend...")
try:
    with urllib.request.urlopen("http://192.168.0.38:8888/fixed_api_main.py", timeout=5) as resp:
        code = resp.read().decode("utf-8")
    with open(api_main_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("   ✅ Updated api/main.py successfully!")
except Exception as e:
    print(f"   ⚠️ Could not fetch from host: {e}")

# 2. Kill any stale process on Port 8008
print("2. Clearing Port 8008...")
os.system("sudo systemctl stop enviromap-api.service 2>/dev/null")
os.system("fuser -k 8008/tcp 2>/dev/null")
time.sleep(1)

# 3. Setup systemd service for 24/7 reliability
service_file = "/etc/systemd/system/enviromap-api.service"
service_content = f"""[Unit]
Description=EnviroMap-KG REST API Backend (Port 8008)
After=network.target

[Service]
Type=simple
User=cse-dept
WorkingDirectory={BASE_DIR}
Environment="PATH={os.path.dirname(VENV_PYTHON)}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart={VENV_PYTHON} {api_main_path}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""

print("3. Starting enviromap-api.service on Port 8008...")
service_started = False
try:
    ret = os.system(f"sudo tee {service_file} >/dev/null << 'EOF'\n{service_content}\nEOF")
    if ret == 0:
        os.system("sudo systemctl daemon-reload")
        os.system("sudo systemctl enable enviromap-api.service 2>/dev/null")
        ret_restart = os.system("sudo systemctl restart enviromap-api.service")
        if ret_restart == 0:
            print("   ✅ enviromap-api.service active via systemd!")
            service_started = True
except Exception as e:
    print(f"   systemd note: {e}")

if not service_started:
    print("   Starting via detached background process...")
    log_path = os.path.join(BASE_DIR, "api.log")
    os.system(f"nohup {VENV_PYTHON} {api_main_path} > {log_path} 2>&1 &")
    print(f"   ✅ Process running in background! Logs at {log_path}")

# 4. Wait for Port 8008 to be ready (takes ~1-2 seconds)
print("4. Testing connection to Port 8008...")
ready = False
for attempt in range(10):
    time.sleep(0.5)
    try:
        req = urllib.request.Request("http://127.0.0.1:8008/health")
        with urllib.request.urlopen(req, timeout=2) as r:
            if r.status == 200:
                print(f"   ✅ Port 8008 responded in {round((attempt+1)*0.5, 1)}s!")
                ready = True
                break
    except Exception:
        pass

# 5. Reload NGINX
os.system("sudo systemctl reload nginx 2>/dev/null")

# 6. Test /api/kg-data through NGINX (Port 80)
print("5. Verifying NGINX Reverse Proxy (http://127.0.0.1/api/kg-data)...")
try:
    with urllib.request.urlopen("http://127.0.0.1/api/kg-data", timeout=5) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        triples = data.get("total_triples", 0)
        observations = data.get("total_observations", 0)
        records = len(data.get("records", []))
        
        print("\n" + "="*60)
        print("🎉 SUCCESS! ENVIROMAP-KG DATA BACKEND IS 100% ONLINE!")
        print("="*60)
        print(f"   📊 RDF Triples:        {triples:,}")
        print(f"   📈 Total Observations: {observations:,}")
        print(f"   🔬 Sensor Records:     {records:,}")
        print(f"   🌐 API Endpoint:       http://192.168.0.21/api/kg-data [200 OK]")
        print(f"   💻 React Dashboard:    http://192.168.0.21/semantic-react/")
        print("="*60)
        print("👉 Now hard-refresh your browser (Ctrl + F5)!")
        print("   All values and graphs will appear immediately on the dashboard!\n")
except Exception as e:
    print(f"\n❌ Error testing proxy: {e}")
    print("Check logs with: journalctl -u enviromap-api.service -n 20 --no-pager")
