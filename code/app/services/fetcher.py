"""Format discovery: query a URL for its available streams."""
import os
import sys
import yt_dlp

from .ytdlp_helpers import YtdlLogger, format_bytes


IS_ANDROID = hasattr(sys, "getandroidapilevel") or "ANDROID_ARGUMENT" in os.environ


class FormatFetcher:

    def fetch(self, url):
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "skip_download": True,
            "logger": YtdlLogger(),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        if IS_ANDROID:
            return self._build_android_options(info)
        return self._build_options(info)

    @staticmethod
    def _build_android_options(info):
        """Pre-merged streams only. No ffmpeg means no merging allowed."""
        formats = info.get("formats", []) or []
        by_height = {}
        for f in formats:
            height = f.get("height")
            if not height:
                continue
            # Must be a progressive stream with both video and audio.
            if f.get("vcodec") in (None, "none"):
                continue
            if f.get("acodec") in (None, "none"):
                continue
            size = f.get("filesize") or f.get("filesize_approx") or 0
            if not size:
                continue
            if by_height.get(height) is None or size > by_height[height][0]:
                by_height[height] = (size, f["format_id"])

        options = []
        for height in sorted(by_height.keys(), reverse=True):
            size, fmt_id = by_height[height]
            options.append(
                (f"{height}p   ~{format_bytes(size)}", fmt_id)
            )

        if not options:
            options.append(("Best available", "best"))

        return options

    @staticmethod
    def _build_options(info):
        formats = info.get("formats", []) or []

        best_audio_size = 0
        for f in formats:
            if f.get("vcodec") == "none" and f.get("acodec") not in (None, "none"):
                s = f.get("filesize") or f.get("filesize_approx") or 0
                if s > best_audio_size:
                    best_audio_size = s

        by_height = {}
        for f in formats:
            height = f.get("height")
            if not height or f.get("vcodec") in (None, "none"):
                continue
            size = f.get("filesize") or f.get("filesize_approx") or 0
            if not size:
                continue
            has_audio = f.get("acodec") not in (None, "none")
            total = size if has_audio else size + best_audio_size
            fmt_id = f["format_id"]
            if has_audio:
                selector = (
                    f"{fmt_id}"
                    f"/best[height={height}][ext=mp4]"
                    f"/best[height={height}]"
                    f"/best"
                )
            else:
                selector = (
                    f"{fmt_id}+bestaudio"
                    f"/bestvideo[height={height}]+bestaudio"
                    f"/bestvideo[height<={height}]+bestaudio"
                    f"/best[height<={height}]"
                    f"/best"
                )
            prev = by_height.get(height)
            if prev is None or total > prev[0]:
                by_height[height] = (total, selector)

        options = []
        for height in sorted(by_height.keys(), reverse=True):
            total, selector = by_height[height]
            options.append((f"{height}p   ~{format_bytes(total)}", selector))

        if not options:
            options.append(("Best available", "bestvideo*+bestaudio/best"))

        return options