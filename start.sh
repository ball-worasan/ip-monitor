#!/bin/sh
set -e

# เริ่ม IP monitor เป็น background
python ip_monitor_refactor.py &

# รัน dashboard ด้วย gunicorn (production-grade)
exec gunicorn dashboard:app --bind 0.0.0.0:8000 --workers 2 --timeout 30

