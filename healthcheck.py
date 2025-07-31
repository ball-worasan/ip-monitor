import requests
import sys
import os

URL = os.getenv("HEALTHCHECK_URL", "http://localhost:8000/health")

try:
    r = requests.get(URL, timeout=3)
    if r.status_code == 200:
        sys.exit(0)
except Exception:
    pass
sys.exit(1)
