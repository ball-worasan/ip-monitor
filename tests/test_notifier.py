import pytest
from notifier import send_line, send_discord
import notifier
from types import SimpleNamespace

class DummyResp:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text

def test_send_line_no_config(monkeypatch, caplog):
    monkeypatch.delenv("LINE_TOKEN", raising=False)
    monkeypatch.delenv("LINE_TARGET_USER_ID", raising=False)
    send_line("test message")
    assert "ข้ามการแจ้งเตือน LINE" in caplog.text or "ไม่ได้กำหนด" in caplog.text

def test_send_discord_no_config(monkeypatch, caplog):
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
    send_discord("test message")
    assert "ข้ามการแจ้งเตือน Discord" in caplog.text or "ไม่ได้ตั้งค่า" in caplog.text
