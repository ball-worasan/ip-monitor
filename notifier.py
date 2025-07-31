import os
import time
import logging
import requests

logger = logging.getLogger("ip_monitor")

LINE_TOKEN = os.getenv("LINE_TOKEN", "").strip()
LINE_TARGET_USER_ID = os.getenv("LINE_TARGET_USER_ID", "").strip()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()

DEFAULT_NOTIFY_ATTEMPTS = int(os.getenv("NOTIFY_MAX_ATTEMPTS", "3"))

session = requests.Session()


def send_line(message: str, max_attempts: int = DEFAULT_NOTIFY_ATTEMPTS) -> None:
    if not LINE_TOKEN or not LINE_TARGET_USER_ID:
        logger.warning("LINE ไม่ได้กำหนด token หรือ target id, ข้ามการแจ้งเตือน LINE")
        return
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": LINE_TARGET_USER_ID,
        "messages": [{"type": "text", "text": message}],
    }
    for attempt in range(1, max_attempts + 1):
        try:
            resp = session.post(
                "https://api.line.me/v2/bot/message/push",
                headers=headers,
                json=payload,
                timeout=5,
            )
            if resp.status_code == 200:
                logger.info(f"ส่ง LINE สำเร็จ: {message}")
                return
            else:
                logger.warning(f"LINE status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"LINE ล้มเหลวครั้งที่ {attempt}: {e}")
        time.sleep(attempt)  # linear backoff
    logger.error(f"ส่ง LINE ไม่สำเร็จหลังจาก {max_attempts} ครั้ง: {message}")


def send_discord(message: str, max_attempts: int = DEFAULT_NOTIFY_ATTEMPTS) -> None:
    if not DISCORD_WEBHOOK_URL:
        logger.warning("Discord webhook ไม่ได้ตั้งค่า, ข้ามการแจ้งเตือน Discord")
        return
    payload = {"content": message}
    headers = {"Content-Type": "application/json"}
    for attempt in range(1, max_attempts + 1):
        try:
            resp = session.post(
                DISCORD_WEBHOOK_URL, json=payload, headers=headers, timeout=5
            )
            if resp.status_code in (200, 204):
                logger.info(f"ส่ง Discord สำเร็จ: {message}")
                return
            else:
                logger.warning(f"Discord status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Discord ล้มเหลวครั้งที่ {attempt}: {e}")
        time.sleep(attempt)
    logger.error(f"ส่ง Discord ไม่สำเร็จหลังจาก {max_attempts} ครั้ง: {message}")
