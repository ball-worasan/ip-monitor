from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger("ip_monitor")


def ensure_dir(file_path: Path):
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)


def read_last_ip(history_path: Path) -> tuple[str | None, str | None]:
    if not history_path.exists():
        return None, None
    try:
        lines = [line.strip() for line in history_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not lines:
            return None, None
        last = lines[-1]
        parts = last.split()
        if len(parts) >= 2:
            timestamp = parts[0]
            ip = parts[-1]
            return timestamp, ip
    except Exception as e:
        logger.warning(f"อ่านประวัติ IP ล้มเหลว: {e}")
    return None, None


def append_history(history_path: Path, ip: str) -> None:
    ensure_dir(history_path)
    ts = datetime.now().astimezone().isoformat()
    try:
        with history_path.open("a", encoding="utf-8") as f:
            f.write(f"{ts} {ip}\n")
    except Exception as e:
        logger.error(f"เพิ่มประวัติ IP ล้มเหลว: {e}")


def tail_history(history_path: Path, n: int = 20) -> list[str]:
    if not history_path.exists():
        return []
    try:
        with history_path.open("r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        return lines[-n:]
    except Exception as e:
        logger.warning(f"อ่าน tail ประวัติล้มเหลว: {e}")
        return []
