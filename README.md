# IP Monitor

ระบบตรวจสอบ Public IP ของเครื่องเป็นระยะ ถ้าพบการเปลี่ยนแปลงจะส่งแจ้งเตือนไปยัง **LINE** และ **Discord**  
บันทึกประวัติ IP, ล็อกเหตุการณ์ทั้งลงไฟล์และแสดงใน stdout, พร้อม dashboard สถานะและ healthcheck — ออกแบบให้รันใน Docker ได้ง่าย

## Features

- ตรวจสอบ Public IP เป็นระยะ (configurable interval)
- ส่งแจ้งเตือนเมื่อ IP เปลี่ยน ผ่าน LINE & Discord (with retry/backoff)
- เก็บประวัติ IP ในไฟล์ (timestamped)
- Logging ทั้งลงไฟล์และ stdout (suitable for Docker)
- Dashboard แสดงสถานะล่าสุดและประวัติล่าสุด พร้อม `/health` endpoint
- Production-grade serving ด้วย Gunicorn
- Named Docker volume เพื่อหลีกเลี่ยงปัญหา permission
- Unit tests (pytest)
- Backup data จาก volume
- (Optional) Token-protected dashboard

## Requirements (local)

- Python 3.11+
- Docker (ถ้าจะรัน containerized)
- Docker Compose (แนะนำสำหรับ deployment แบบสะดวก)
- `make` หรือ shell (ถ้าจะเขียนสคริปต์ช่วยเหลือ)
- LINE Messaging API token & target ID
- Discord webhook URL

## Quickstart (local dev)

```bash
# สร้าง virtualenv และ activate
python -m venv .venv
source .venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt

# คัดลอก template แล้วแก้ .env
cp .env.template .env
# แก้ค่าภายใน .env (LINE_TOKEN, LINE_TARGET_USER_ID, DISCORD_WEBHOOK_URL ฯลฯ)

# รันแบบแยก
python ip_monitor_refactor.py         # monitor
python dashboard.py                  # dashboard (http://localhost:8000)

# สร้าง/รีบิลด์ และรันเป็น background
docker compose up -d --build

# ดู log ของ service
docker compose logs -f ip-monitor

# หยุด/ลบ และ clean
docker compose down

# อัปเดต image แล้วรีโหลด
docker compose pull
docker compose up -d --build

# ดูสถานะ health
curl http://localhost:8000/health
