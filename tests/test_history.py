from history import append_history, read_last_ip, tail_history
from pathlib import Path
import tempfile

def test_history_append_and_read(tmp_path):
    hist = tmp_path / "h.log"
    append_history(hist, "8.8.8.8")
    ts, ip = read_last_ip(hist)
    assert ip == "8.8.8.8"
    tail = tail_history(hist, 1)
    assert len(tail) == 1
    assert "8.8.8.8" in tail[0]
