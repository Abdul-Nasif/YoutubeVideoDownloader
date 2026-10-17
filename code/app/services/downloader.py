"""Download service: wraps yt-dlp for a single download.

The service is UI-agnostic. It reports back through three callbacks that
the caller is free to schedule onto whatever thread it likes:
    on_progress(percent: float, speed_str: str)
    on_finished()
    on_error(message: str)
"""
import os
import sys

import yt_dlp

from .ytdlp_helpers import YtdlLogger, format_speed


# Detect Android at import time. python-for-android sets these markers.
IS_ANDROID = (
    hasattr(sys, "getandroidapilevel")
    or "ANDROID_ARGUMENT" in os.environ
    or "ANDROID_ROOT" in os.environ
)


def _ffmpeg_dir():
    """Return the folder containing the bundled ffmpeg, or None.

    Checks two locations:
      1. sys._MEIPASS/assets/ffmpeg  - PyInstaller temp extraction dir
      2. <repo>/assets/ffmpeg        - running from source
    """
    # PyInstaller sets sys._MEIPASS to its runtime extraction directory.
    base = getattr(sys, "_MEIPASS", None)
    if base:
        candidate = os.path.join(base, "assets", "ffmpeg")
        if os.path.isdir(candidate):
            return candidate

    # Running from source: walk up from this file to the project root.
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(here))
    candidate = os.path.join(project_root, "assets", "ffmpeg")
    if os.path.isdir(candidate):
        return candidate

    return None


class DownloadService:

    def __init__(self, on_progress=None, on_finished=None, on_error=None):
        self.on_progress = on_progress
        self.on_finished = on_finished
        self.on_error = on_error

    def download(self, url, output_dir, filename, format_selector,
                 output_format="mp4"):
        outtmpl = os.path.join(
            output_dir,
            (filename if filename else "%(title)s") + ".%(ext)s",
        )

        ydl_opts = {
            "outtmpl": outtmpl,
            "remote_components": "ejs:github",
            "progress_hooks": [self._hook],
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "logger": YtdlLogger(),
        }

        # Point yt-dlp at the bundled ffmpeg if we have one.
        ff = _ffmpeg_dir()
        if ff:
            ydl_opts["ffmpeg_location"] = ff

        if output_format == "mp3":
            if IS_ANDROID and not ff:
                # No ffmpeg on this Android build: grab native m4a audio.
                ydl_opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
            else:
                # Desktop or Android with ffmpeg: extract to MP3 at 192 kbps.
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
        else:
            if IS_ANDROID and not ff:
                # No ffmpeg: only pre-merged streams work.
                ydl_opts["format"] = (
                    "best[ext=mp4]"
                    "/best[height<=720][ext=mp4]"
                    "/best"
                )
            else:
                # Desktop or Android with ffmpeg: full quality with merging.
                ydl_opts["format"] = format_selector
                ydl_opts["merge_output_format"] = "mp4"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as exc:
            raw = str(exc).strip()
            msg = raw.splitlines()[0] if raw else "Unknown error"
            if len(msg) > 140:
                msg = msg[:137] + "..."
            if self.on_error:
                self.on_error(msg)
            return

        if self.on_finished:
            self.on_finished()

    def _hook(self, d):
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes") or 0
            percent = (downloaded / total * 100.0) if total else 0.0
            speed = format_speed(d.get("speed") or 0)
            if self.on_progress:
                self.on_progress(percent, speed)
        elif status == "finished":
            # Bytes are done; postprocessing may still follow.
            if self.on_progress:
                self.on_progress(100.0, "")