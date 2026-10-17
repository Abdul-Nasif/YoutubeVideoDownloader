"""Shared yt-dlp plumbing: logger, stream guard, formatters."""
import io
import sys


class YtdlLogger:
    """Silence yt-dlp; the UI is driven by callbacks instead of stdout."""
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


def ensure_streams():
    """Under pyinstaller --windowed (and some IDE runners) sys.stdout /
    sys.stderr can be None or a str, and yt-dlp calls .write() on them."""
    if sys.stdout is None or not hasattr(sys.stdout, "write"):
        sys.stdout = io.StringIO()
    if sys.stderr is None or not hasattr(sys.stderr, "write"):
        sys.stderr = io.StringIO()


def format_bytes(size):
    if not size:
        return "?"
    v = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if v < 1024:
            return f"{v:.1f} {unit}"
        v /= 1024.0
    return f"{v:.1f} TB"


def format_speed(bps):
    if not bps:
        return ""
    units = ("B/s", "KB/s", "MB/s", "GB/s")
    i, v = 0, float(bps)
    while v >= 1024 and i < len(units) - 1:
        v /= 1024.0
        i += 1
    return f"{v:.1f} {units[i]}"