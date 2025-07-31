import time
import random
import socket
import logging
from typing import Optional
import requests

logger = logging.getLogger("ip_monitor")

# retry/backoff decorator
def retry_with_backoff(
    max_attempts: int = 5,
    base_delay: float = 1.0,
    factor: float = 2.0,
    max_delay: float = 30.0,
    jitter: float = 0.1,
):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt == max_attempts:
                        logger.debug(f"สุดท้ายของ retry {fn.__name__} ล้มเหลว: {e}")
                        raise
                    sleep_time = min(delay, max_delay)
                    # add jitter +/- percentage
                    sleep_time = sleep_time * (1 + random.uniform(-jitter, jitter))
                    logger.debug(
                        f"{fn.__name__} ล้มเหลวครั้งที่ {attempt}, จะลองใหม่ใน {sleep_time:.2f}s: {e}"
                    )
                    time.sleep(sleep_time)
                    delay *= factor
            raise last_exc  # pragma: no cover
        return wrapper
    return decorator


def check_connectivity() -> bool:
    try:
        with socket.create_connection(("8.8.8.8", 53), timeout=2):
            return True
    except Exception:
        return False


@retry_with_backoff()
def fetch_public_ip(session: requests.Session, services: list[str]) -> str:
    last_err = None
    for url in services:
        try:
            if "?format=json" in url:
                r = session.get(url, timeout=5)
                r.raise_for_status()
                data = r.json()
                ip = data.get("ip", "").strip()
            else:
                r = session.get(url, timeout=5)
                r.raise_for_status()
                ip = r.text.strip()
            if ip:
                cleaned = ip.split()[0]
                if all(c.isdigit() or c == "." for c in cleaned):
                    return cleaned
                else:
                    logger.warning(f"IP ที่ได้จาก {url} รูปแบบผิด: {ip}")
            else:
                logger.warning(f"ได้ค่าว่างจาก {url}")
        except Exception as e:
            last_err = e
            logger.debug(f"ล้มเหลวในการดึงจาก {url}: {e}")
    raise RuntimeError(f"ไม่สามารถหาที่อยู่ IP ได้ (error ล่าสุด: {last_err})")
