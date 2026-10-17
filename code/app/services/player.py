"""Open and reveal files with the OS's default handlers."""
import os
import subprocess
import sys


def open_file(path):
    """Play a file with the system default application."""
    if not os.path.exists(path):
        return False, "File not found."
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True, ""
    except Exception as exc:
        return False, str(exc)


def open_folder(path):
    """Open a folder in the OS file browser."""
    if not os.path.isdir(path):
        return False, "Folder not found."
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True, ""
    except Exception as exc:
        return False, str(exc)


def reveal_in_folder(path):
    """Highlight a file in the OS file browser. Falls back to opening
    the containing folder if the exact selection is not supported."""
    if not os.path.exists(path):
        # Fall back to opening the parent folder rather than failing.
        parent = os.path.dirname(path)
        if os.path.isdir(parent):
            return open_folder(parent)
        return False, "File not found."
    try:
        if sys.platform.startswith("win"):
            subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", path])
        else:
            subprocess.Popen(["xdg-open", os.path.dirname(path)])
        return True, ""
    except Exception as exc:
        return False, str(exc)