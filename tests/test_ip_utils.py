import pytest
import requests
from ip_utils import fetch_public_ip, check_connectivity

class DummyResponse:
    def __init__(self, text="", status_code=200, json_data=None):
        self.text = text
        self.status_code = status_code
        self._json = json_data or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")

    def json(self):
        return self._json

def test_fetch_public_ip_success(monkeypatch):
    session = requests.Session()
    calls = []

    def fake_get(url, timeout):
        calls.append(url)
        if "ipify" in url:
            return DummyResponse(json_data={"ip": "1.2.3.4"})
        raise RuntimeError("should not reach")

    monkeypatch.setattr(session, "get", fake_get)
    ip = fetch_public_ip(session, ["https://api.ipify.org?format=json"])
    assert ip == "1.2.3.4"

def test_check_connectivity(monkeypatch):
    # ถ้าไม่ล้มเหลวถือว่าเป็น bool
    assert isinstance(check_connectivity(), bool)
