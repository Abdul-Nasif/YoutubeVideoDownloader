"""Open the OS-native folder picker.

On Windows, we shell out to PowerShell and use the built-in
System.Windows.Forms.FolderBrowserDialog. That works in both source runs
and PyInstaller bundles, unlike tkinter subprocess approaches which
re-launch the frozen EXE and confuse Kivy's argument parser.
"""
import os
import subprocess
import sys


_PS_SCRIPT = (
    "Add-Type -AssemblyName System.Windows.Forms;"
    "$f = New-Object System.Windows.Forms.FolderBrowserDialog;"
    "$f.Description = 'Select download folder';"
    "$f.SelectedPath = '__INITIAL__';"
    "$f.ShowNewFolderButton = $true;"
    "$r = $f.ShowDialog();"
    "if ($r -eq [System.Windows.Forms.DialogResult]::OK) "
    "{ Write-Output $f.SelectedPath }"
)

_TK_SCRIPT = r"""
import sys
try:
    import tkinter as tk
    from tkinter import filedialog
except Exception as exc:
    sys.stderr.write("tkinter-missing: " + str(exc) + "\n")
    sys.exit(2)

root = tk.Tk()
root.withdraw()
try:
    root.attributes("-topmost", True)
except Exception:
    pass

initial = __INITIAL_DIR__
try:
    path = filedialog.askdirectory(initialdir=initial, mustexist=False)
except Exception as exc:
    sys.stderr.write("dialog-error: " + str(exc) + "\n")
    sys.exit(3)

print(path or "")
"""


def pick_folder(initial=None):
    """Open the native folder chooser.

    Returns the chosen directory as a string, or None if the user
    cancelled or the picker is unavailable.
    """
    if initial is None or not os.path.isdir(initial):
        initial = os.path.expanduser("~")

    if sys.platform.startswith("win"):
        return _pick_windows(initial)
    if sys.platform == "darwin":
        return _pick_macos(initial)
    return _pick_linux(initial)


# ---------------------------------------------------------------------------
# Windows: PowerShell + System.Windows.Forms.FolderBrowserDialog
# ---------------------------------------------------------------------------

def _pick_windows(initial):
    # Escape single quotes for a PowerShell single-quoted string.
    escaped = initial.replace("'", "''")
    script = _PS_SCRIPT.replace("__INITIAL__", escaped)

    kwargs = {
        "args": ["powershell", "-NoProfile", "-STA", "-Command", script],
        "capture_output": True,
        "text": True,
    }
    # Hide the brief console window that would otherwise flash.
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        kwargs["creationflags"] = 0x08000000

    try:
        result = subprocess.run(**kwargs)
    except Exception:
        return None

    if result.returncode != 0:
        return None

    path = (result.stdout or "").strip()
    if not path:
        return None
    path = os.path.normpath(path)
    return path if os.path.isdir(path) else None


# ---------------------------------------------------------------------------
# macOS / Linux: tkinter in a child Python interpreter
# ---------------------------------------------------------------------------

def _pick_macos(initial):
    return _pick_tk(initial)


def _pick_linux(initial):
    return _pick_tk(initial)


def _pick_tk(initial):
    script = _TK_SCRIPT.replace("__INITIAL_DIR__", repr(initial))

    kwargs = {
        "args": [sys.executable, "-c", script],
        "capture_output": True,
        "text": True,
    }
    try:
        result = subprocess.run(**kwargs)
    except Exception:
        return None

    if result.returncode != 0:
        return None

    path = (result.stdout or "").strip()
    if not path:
        return None
    path = os.path.normpath(path)
    return path if os.path.isdir(path) else None