import os
import sys
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

from ip_utils import fetch_public_ip, check_connectivity
from notifier import send_line, send_discord
from history import read_last_ip, append_history

import requests

# === load config ===
load_dotenv()

# paths
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
LOG_FILE = Path(os.getenv("LOG_FILE", DATA_DIR / "ip_monitor.log"))
IP_HISTORY_FILE = Path(os.getenv("IP_HISTORY_FILE", DATA_DIR / "ip_history.log"))


def get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default))
    # ตัดคอมเมนต์หลัง '#' ออก, แล้ว strip
    cleaned = raw.split("#", 1)[0].strip()
    try:
        return int(cleaned)
    except ValueError:
        logger.warning(f"ตัวแปร {name} เป็นค่าไม่ถูกต้อง ({raw}), ใช้ default={default}")
        return default


CHECK_INTERVAL = get_env_int("CHECK_INTERVAL", 300)


PUBLIC_IP_SERVICES = [
    "https://api.ipify.org?format=json",
    "https://ifconfig.me/ip",
    "https://ident.me",
]

# === logging ===
logger = logging.getLogger("ip_monitor")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z"
)

# ensure directories
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

file_handler = logging.StreamHandler(sys.stdout)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# also write to file
try:
    from logging.handlers import RotatingFileHandler

    fh = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
except Exception:
    logger.warning("ไม่สามารถตั้งค่า file handler ได้")

session = requests.Session()

def craft_message(old_ip: str | None, new_ip: str) -> str:
    if old_ip is None:
        return f"🟢 Public IP ตรวจพบครั้งแรก: {new_ip}"
    elif old_ip != new_ip:
        return f"🔄 Public IP เปลี่ยน: {old_ip} → {new_ip}"
    else:
        return ""

def run():
    logger.info(f"เริ่มระบบตรวจสอบ public IP (interval={CHECK_INTERVAL}s)")
    last_ts, last_ip = read_last_ip(IP_HISTORY_FILE)
    if last_ip:
        logger.info(f"IP ก่อนหน้า: {last_ip} (บันทึกเมื่อ {last_ts})")
    else:
        logger.info("ยังไม่มี IP เก็บไว้ในประวัติ (เริ่มต้นครั้งแรก)")

    try:
        while True:
            if not check_connectivity():
                logger.warning("ไม่มีการเชื่อมต่ออินเทอร์เน็ต, รอ 60 วินาที")
                time.sleep(60)
                continue

            try:
                ip = fetch_public_ip(session, PUBLIC_IP_SERVICES)
            except Exception as e:
                logger.warning(f"ดึง public IP ไม่สำเร็จ: {e}")
                time.sleep(60)
                continue

            if ip != last_ip:
                msg = craft_message(last_ip, ip)
                if msg:
                    logger.info(msg)
                    append_history(IP_HISTORY_FILE, ip)
                    send_line(msg)
                    send_discord(msg)
                    last_ip = ip
            else:
                logger.debug(f"IP ยังไม่เปลี่ยน: {ip}")

            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        logger.info("รับสัญญาณหยุด, ออกอย่างสุภาพ")
    except Exception as e:
        logger.exception(f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")

if __name__ == "__main__":
    run()
