import os
import threading
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ListProperty, StringProperty
from kivy.uix.screenmanager import Screen

from app.services.folder_picker import pick_folder
from app.services.library import LibraryService
from app.services.player import open_folder
from app.services.ytdlp_helpers import format_bytes


class LibraryScreen(Screen):

    rv_data = ListProperty([])
    folder = StringProperty("")
    status_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._picking = False

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh(), 0)

    def refresh(self):
        app = App.get_running_app()
        folder = app.download_dir if app else ""
        self.folder = folder

        try:
            items = LibraryService.list_files(folder)
        except Exception as exc:
            self.rv_data = []
            self.status_text = f"Failed to scan folder: {exc}"
            return

        self.rv_data = [
            {
                "filename": it["filename"],
                "path": it["path"],
                "size_str": format_bytes(it["size"]),
                "date_str": time.strftime(
                    "%Y-%m-%d %H:%M", time.localtime(it["mtime"])
                ),
            }
            for it in items
        ]

        stamp = time.strftime("%H:%M:%S")
        if not folder:
            self.status_text = "No download folder set."
        elif not os.path.isdir(folder):
            self.status_text = f"Folder does not exist: {folder}"
        elif not self.rv_data:
            self.status_text = f"No media found in {folder} - refreshed {stamp}"
        else:
            self.status_text = (
                f"{len(self.rv_data)} file(s) in {folder} - refreshed {stamp}"
            )

    # ---- folder actions ---------------------------------------------

    def open_current_folder(self):
        app = App.get_running_app()
        if not app or not app.download_dir:
            self.status_text = "No download folder set."
            return
        if not os.path.isdir(app.download_dir):
            self.status_text = f"Folder does not exist: {app.download_dir}"
            return
        ok, err = open_folder(app.download_dir)
        if not ok:
            self.status_text = f"Cannot open folder: {err}"

    def change_folder(self):
        if self._picking:
            return
        app = App.get_running_app()
        start = app.download_dir if app else os.path.expanduser("~")
        if not start or not os.path.isdir(start):
            start = os.path.expanduser("~")

        self._picking = True
        self.status_text = "Waiting for folder selection..."
        threading.Thread(
            target=self._pick_worker, args=(start,), daemon=True
        ).start()

    def _pick_worker(self, start):
        path = pick_folder(start)
        Clock.schedule_once(lambda dt: self._on_folder_picked(path), 0)

    def _on_folder_picked(self, path):
        self._picking = False
        if not path:
            self.refresh()
            return
        app = App.get_running_app()
        if app:
            app.download_dir = path
        # Also reflect the new folder on the Download screen.
        sm = self.manager
        if sm and "download" in sm.screen_names:
            dl = sm.get_screen("download")
            fi = dl.ids.get("folder_input")
            if fi is not None:
                fi.text = path
        self.refresh()