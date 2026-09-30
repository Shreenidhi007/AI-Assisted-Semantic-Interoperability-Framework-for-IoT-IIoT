#!/usr/bin/env python3
"""
Test of resilient Python HTTP server on port 8009
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/kg-data"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            data = {
                "status": "success",
                "total_triples": 1045274,
                "total_observations": 61186,
                "records": [{"concept": "Temperature", "value": 24.5, "domain": "hydroponics"}]
            }
            self.wfile.write(json.dumps(data).encode("utf-8"))
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "healthy"}')
        else:
            self.send_response(404)
            self.end_headers()

server = HTTPServer(("127.0.0.1", 8009), APIHandler)
t = Thread(target=server.serve_forever, daemon=True)
t.start()
print("Server started on 8009!")

import urllib.request
with urllib.request.urlopen("http://127.0.0.1:8009/api/kg-data") as r:
    res = json.loads(r.read().decode())
    print("Response status:", r.status, "| Triples:", res["total_triples"])
server.shutdown()
print("Server test passed!")

