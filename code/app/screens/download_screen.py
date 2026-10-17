import os
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

from app.config import ERROR, INFO, SUCCESS
from app.services.downloader import DownloadService
from app.services.fetcher import FormatFetcher
from app.services.folder_picker import pick_folder


class DownloadScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._format_map = {}
        self._fetching = False
        self._picking = False
        self.output_format = "mp4"

    def on_enter(self):
        Clock.schedule_once(self._sync_folder, 0)

    def _sync_folder(self, _dt):
        folder_input = self.ids.get("folder_input")
        if folder_input is None:
            return
        if not folder_input.text:
            app = App.get_running_app()
            if app:
                folder_input.text = app.download_dir

    # ---- status ------------------------------------------------------

    def set_status(self, text, kind="info"):
        label = self.ids.status_label
        label.text = text
        label.color = {"error": ERROR, "success": SUCCESS}.get(kind, INFO)

    # ---- format toggle ----------------------------------------------

    def on_format_chip(self, fmt, state):
        if state != "down":
            return
        if fmt == self.output_format:
            return
        self.set_output_format(fmt)

    def set_output_format(self, fmt):
        self.output_format = fmt
        ids = self.ids

        display = ids.get("format_display")
        if display is not None:
            display.text = "Audio (MP3)" if fmt == "mp3" else "Video (MP4)"

        if fmt == "mp3":
            ids.quality_spinner.values = ["Auto (best audio)"]
            ids.quality_spinner.text = "Auto (best audio)"
            self._format_map = {"Auto (best audio)": "bestaudio/best"}
            ids.fetch_btn.disabled = True
            self.set_status(
                "MP3 mode: audio will be extracted at 192 kbps.", "info"
            )
        else:
            ids.quality_spinner.values = []
            ids.quality_spinner.text = "Fetch formats first"
            self._format_map = {}
            ids.fetch_btn.disabled = False
            self.set_status(
                "MP4 mode: click Fetch to load quality options.", "info"
            )

    # ---- native folder picker ---------------------------------------

    def open_folder_chooser(self):
        if self._picking:
            return

        ids = self.ids
        start = ids.folder_input.text.strip()
        if not start or not os.path.isdir(start):
            start = os.path.expanduser("~")

        self._picking = True
        self.set_status("Waiting for folder selection...", "info")

        # The picker blocks until the user chooses.  Run it off the main
        # thread so the Kivy UI stays responsive.
        threading.Thread(
            target=self._pick_folder_worker,
            args=(start,),
            daemon=True,
        ).start()

    def _pick_folder_worker(self, start):
        path = pick_folder(start)
        Clock.schedule_once(lambda dt: self._on_folder_picked(path), 0)

    def _on_folder_picked(self, path):
        self._picking = False
        if not path:
            self.set_status("Folder selection cancelled.", "info")
            return

        self.ids.folder_input.text = path
        app = App.get_running_app()
        if app:
            app.download_dir = path
        self.set_status(f"Folder set: {path}", "success")

    # ---- fetch formats (MP4 only) ----------------------------------

    def fetch_formats(self):
        if self._fetching:
            return

        if self.output_format == "mp3":
            self.set_status(
                "MP3 mode uses best audio automatically; just click Download.",
                "info",
            )
            return

        ids = self.ids
        raw_url = ids.url_input.text.strip()
        if not raw_url:
            self.set_status("Please enter a URL first.", "error")
            return

        url = self._normalize_url(raw_url)
        self._fetching = True
        ids.fetch_btn.disabled = True
        ids.fetch_btn.text = "..."
        ids.quality_spinner.values = []
        ids.quality_spinner.text = "Fetching..."
        self.set_status("Fetching available formats...", "info")

        threading.Thread(target=self._fetch_worker, args=(url,), daemon=True).start()

    def _fetch_worker(self, url):
        try:
            options = FormatFetcher().fetch(url)
        except Exception as exc:
            raw = str(exc).strip()
            msg = raw.splitlines()[0] if raw else "Unknown error"
            if len(msg) > 110:
                msg = msg[:107] + "..."
            Clock.schedule_once(lambda dt: self._on_fetch_error(msg), 0)
            return
        Clock.schedule_once(lambda dt: self._populate_spinner(options), 0)

    def _populate_spinner(self, options):
        self._fetching = False
        ids = self.ids
        ids.fetch_btn.disabled = False
        ids.fetch_btn.text = "Fetch"

        if not options:
            ids.quality_spinner.text = "No formats found"
            self.set_status("No downloadable formats found.", "error")
            return

        self._format_map = dict(options)
        labels = [label for label, _ in options]
        ids.quality_spinner.values = labels
        ids.quality_spinner.text = labels[0]
        self.set_status(
            f"Found {len(labels)} quality options. Pick one and download.",
            "info",
        )

    def _on_fetch_error(self, msg):
        self._fetching = False
        ids = self.ids
        ids.fetch_btn.disabled = False
        ids.fetch_btn.text = "Fetch"
        ids.quality_spinner.text = "Fetch failed"
        self.set_status(f"Failed to fetch formats: {msg}", "error")

    # ---- download ---------------------------------------------------

    def start_download(self):
        ids = self.ids
        raw_url = ids.url_input.text.strip()
        folder = ids.folder_input.text.strip()
        name = ids.name_input.text.strip()

        if not raw_url:
            self.set_status("Please enter a video URL.", "error")
            return

        url = self._normalize_url(raw_url)

        if not folder:
            app = App.get_running_app()
            folder = app.download_dir if app else os.path.expanduser("~")
            ids.folder_input.text = folder

        try:
            os.makedirs(folder, exist_ok=True)
        except Exception as exc:
            self.set_status(f"Cannot create folder: {exc}", "error")
            return

        if name:
            name = name.replace("/", "_").replace("\\", "_").strip()

        selector = self._format_map.get(ids.quality_spinner.text)
        if not selector:
            if self.output_format == "mp3":
                selector = "bestaudio/best"
            else:
                self.set_status(
                    "Please fetch formats and choose a quality first.", "error"
                )
                return

        app = App.get_running_app()
        if app:
            app.download_dir = folder

        ids.download_btn.disabled = True
        ids.download_btn.text = "Downloading..."
        ids.progress.value = 0
        ids.percent_label.text = "0%"
        ids.speed_label.text = ""
        self.set_status(
            f"Starting {self.output_format.upper()} download...", "info"
        )

        service = DownloadService(
            on_progress=self._on_progress_bg,
            on_finished=self._on_finished_bg,
            on_error=self._on_error_bg,
        )

        threading.Thread(
            target=service.download,
            args=(url, folder, name, selector, self.output_format),
            daemon=True,
        ).start()

    # ---- thread bridges ---------------------------------------------

    def _on_progress_bg(self, percent, speed):
        Clock.schedule_once(lambda dt: self._update_progress(percent, speed), 0)

    def _on_finished_bg(self):
        Clock.schedule_once(lambda dt: self._on_success(), 0)

    def _on_error_bg(self, msg):
        Clock.schedule_once(lambda dt: self._on_error(msg), 0)

    # ---- UI updates -------------------------------------------------

    def _update_progress(self, percent, speed_str):
        ids = self.ids
        ids.progress.value = percent
        ids.percent_label.text = f"{percent:.0f}%"
        ids.speed_label.text = speed_str

    def _on_success(self):
        ids = self.ids
        ids.progress.value = 100
        ids.percent_label.text = "100%"
        ids.speed_label.text = ""
        ids.download_btn.disabled = False
        ids.download_btn.text = "Download"
        self.set_status("Download completed successfully.", "success")

        sm = self.manager
        if sm and "library" in sm.screen_names:
            sm.get_screen("library").refresh()

    def _on_error(self, msg):
        ids = self.ids
        ids.download_btn.disabled = False
        ids.download_btn.text = "Download"
        ids.progress.value = 0
        ids.percent_label.text = "0%"
        ids.speed_label.text = ""
        self.set_status(f"Error: {msg}", "error")

    # ---- utils ------------------------------------------------------

    @staticmethod
    def _normalize_url(raw):
        if raw.startswith(("http://", "https://")):
            return raw
        return "https://" + raw