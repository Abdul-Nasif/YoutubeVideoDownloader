"""Application-wide constants and the design palette."""
import os

APP_NAME = "YouTube Downloader"
WINDOW_SIZE = (620, 820)
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
APP_ICON = os.path.join(ASSETS_DIR, "icon.png")
APP_VERSION = "1.0.0"
APP_AUTHOR = "Abdul Raqueb Nasif"
APP_DESCRIPTION = "Download and manage YouTube videos and audio."
APP_COPYRIGHT = "© 2026 Abdul Raqueb Nasif"
PACKAGE_NAME = "ytdownloader"
PACKAGE_DOMAIN = "com.nasif"

# Palette (RGBA, 0-1)
BG      = (0.043, 0.043, 0.051, 1)
SURFACE = (0.082, 0.082, 0.094, 1)
BORDER  = (0.157, 0.157, 0.176, 1)
TEXT    = (0.96, 0.96, 0.97, 1)
MUTED   = (0.52, 0.52, 0.58, 1)
HINT    = (0.36, 0.36, 0.41, 1)
ERROR   = (0.97, 0.45, 0.45, 1)
SUCCESS = (0.36, 0.85, 0.55, 1)
INFO    = (0.55, 0.55, 0.60, 1)

VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".webm", ".mov", ".avi",
    ".flv", ".m4v", ".ts", ".3gp",
}

AUDIO_EXTENSIONS = {
    ".mp3", ".m4a", ".aac", ".opus", ".ogg", ".flac", ".wav", ".wma",
}

MEDIA_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS