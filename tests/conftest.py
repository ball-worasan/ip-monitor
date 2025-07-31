import sys
import pathlib

# เพิ่ม root ของโปรเจกต์ ให้อยู่ใน import path เวลาเทสต์จาก tests/
root = pathlib.Path(__file__).parent.parent.resolve()
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import pytest
from pathlib import Path
import os

@pytest.fixture
def temp_history_file(tmp_path):
    f = tmp_path / "history.log"
    return f

@pytest.fixture(autouse=True)
def isolate_env(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("IP_HISTORY_FILE", str(tmp_path / "data" / "ip_history.log"))

