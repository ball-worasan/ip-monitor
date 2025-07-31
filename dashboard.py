import os
from flask import Flask, jsonify, render_template_string
from pathlib import Path
from history import read_last_ip, tail_history
from datetime import datetime

app = Flask(__name__)

IP_HISTORY_FILE = Path(os.getenv("IP_HISTORY_FILE", "./data/ip_history.log"))

TEMPLATE = """
<!doctype html>
<title>IP Monitor Dashboard</title>
<style>
body { font-family: system-ui, sans-serif; padding: 1rem; background: #f5f5f5; }
.card { background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom:1rem; }
h1 { margin-top:0; }
table { width:100%; border-collapse: collapse; }
td, th { padding:8px; border-bottom:1px solid #e0e0e0; }
.small { color: #555; font-size: 0.9em; }
</style>
<h1>IP Monitor Dashboard</h1>
<div class="card">
  <h2>สถานะล่าสุด</h2>
  {% if last_ip %}
    <p><strong>Public IP:</strong> {{ last_ip }}</p>
    <p class="small">บันทึกเมื่อ: {{ last_ts }} (ผ่านมา {{ age }} วินาที)</p>
  {% else %}
    <p>ยังไม่มี IP ถูกเก็บไว้</p>
  {% endif %}
</div>
<div class="card">
  <h2>ประวัติล่าสุด ({{ history|length }})</h2>
  <table>
    <tr><th>Timestamp</th><th>IP</th></tr>
    {% for line in history %}
      {% set parts = line.split() %}
      <tr><td>{{ parts[0] }}</td><td>{{ parts[1] if parts|length >1 else '' }}</td></tr>
    {% endfor %}
  </table>
</div>
<div class="card">
  <h2>Health</h2>
  <p>Status: <strong>OK</strong></p>
</div>
"""

def compute_age(ts_str):
    try:
        ts = datetime.fromisoformat(ts_str)
        delta = datetime.now(ts.tzinfo) - ts
        return int(delta.total_seconds())
    except Exception:
        return None

@app.route("/health")
def health():
    last_ts, last_ip = read_last_ip(IP_HISTORY_FILE)
    age = compute_age(last_ts) if last_ts else None
    return jsonify(
        status="ok",
        last_ip=last_ip,
        last_update_age_seconds=age,
    )

@app.route("/")
def index():
    last_ts, last_ip = read_last_ip(IP_HISTORY_FILE)
    age = compute_age(last_ts) if last_ts else None
    history = tail_history(IP_HISTORY_FILE, 20)
    return render_template_string(
        TEMPLATE,
        last_ip=last_ip,
        last_ts=last_ts,
        age=age,
        history=history,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("DASHBOARD_PORT", "8000")), debug=False)
