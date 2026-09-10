#!/usr/bin/env python3
"""Seed the database with sample complaints from seed_complaints.json.
Usage: python seed.py [API_BASE_URL]
Default URL: http://localhost:8000/api
"""
import json, sys, urllib.request, urllib.error
from pathlib import Path

url = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/api").rstrip("/")
data = json.loads(Path(__file__).parent / "seed_complaints.json").read_text() \
    if False else (Path(__file__).parent / "seed_complaints.json").read_text()
complaints = json.loads(data)

for i, c in enumerate(complaints, 1):
    body = json.dumps(c).encode()
    req = urllib.request.Request(f"{url}/complaints", data=body,
                                  headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read())
            print(f"[{i}/{len(complaints)}] ✓ {result['complaint_number']} — {c['customer_name']} ({c['risk_level']})")
    except urllib.error.HTTPError as e:
        print(f"[{i}/{len(complaints)}] ✗ {c['customer_name']}: HTTP {e.code} — {e.read().decode()}")
    except urllib.error.URLError as e:
        print(f"[{i}/{len(complaints)}] ✗ Could not connect to {url}: {e.reason}")
        sys.exit(1)

print("\nDone. Refresh the dashboard at http://localhost:5173")
