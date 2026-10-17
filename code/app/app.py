import os

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from app import widgets as _widgets    # noqa: F401
from app import screens as _screens    # noqa: F401
from app import kv

from app.config import APP_ICON, APP_NAME, WINDOW_SIZE, DEFAULT_DOWNLOAD_DIR
from app.services.library import LibraryService
from app.services.player import open_file, reveal_in_folder
from app.services.ytdlp_helpers import ensure_streams
from app.widgets.confirm_popup import ConfirmPopup


class RootWidget(BoxLayout):
    """Top-level layout: header, screen manager, footer."""

    def go_to(self, name):
        sm = self.ids.sm
        if name not in sm.screen_names:
            return
        sm.current = name
        self.ids.nav_download.selected = (name == "download")
        self.ids.nav_library.selected = (name == "library")


class DownloaderApp(App):

    download_dir = StringProperty(DEFAULT_DOWNLOAD_DIR)

    def build(self):
        ensure_streams()
        self.title = APP_NAME
        self.icon = APP_ICON
        Window.size = WINDOW_SIZE
        Window.clearcolor = (0.035, 0.035, 0.043, 1)

        kv.load_all()

        return RootWidget()

    def on_start(self):
        dl = self.root.ids.sm.get_screen("download")
        dl.ids.folder_input.text = self.download_dir

    # ---- library actions --------------------------------------------

    def play_file(self, path):
        ok, err = open_file(path)
        if not ok:
            self._lib_status(f"Cannot open: {err}")

    def reveal_file(self, path):
        ok, err = reveal_in_folder(path)
        if not ok:
            self._lib_status(f"Cannot reveal: {err}")

    def delete_library_file(self, path):
        filename = os.path.basename(path)

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(14),
            padding=dp(20),
        )

        message = Label(
            text=(
                f"[b]{filename}[/b]\n\n"
                "This file will be permanently deleted from disk.\n"
                "This action cannot be undone."
            ),
            markup=True,
            color=(0.96, 0.96, 0.97, 1),
            font_size=sp(13),
            halign="left",
            valign="top",
            text_size=(dp(300), dp(90)),
            size_hint=(1, None),
            height=dp(90),
        )
        content.add_widget(message)

        row = BoxLayout(
            size_hint=(1, None),
            height=dp(40),
            spacing=dp(10),
        )

        cancel_btn = Button(
            text="Cancel",
            background_normal="",
            background_down="",
            background_color=(0.15, 0.15, 0.17, 1),
            color=(0.96, 0.96, 0.97, 1),
            font_size=sp(13),
        )

        delete_btn = Button(
            text="Delete permanently",
            background_normal="",
            background_down="",
            background_color=(0.85, 0.28, 0.28, 1),
            color=(0.96, 0.96, 0.97, 1),
            font_size=sp(13),
            bold=True,
        )

        row.add_widget(cancel_btn)
        row.add_widget(delete_btn)
        content.add_widget(row)

        popup = ConfirmPopup(content=content)

        cancel_btn.bind(on_release=popup.dismiss)

        def do_delete(*_):
            popup.dismiss()
            ok, err = LibraryService.delete_file(path)
            if ok:
                self._refresh_library()
                self._lib_status(f"Deleted: {filename}")
            else:
                self._lib_status(f"Cannot delete: {err}")

        delete_btn.bind(on_release=do_delete)
        popup.open()

    # ---- internal ----------------------------------------------------

    def _refresh_library(self):
        sm = self.root.ids.sm
        if "library" in sm.screen_names:
            sm.get_screen("library").refresh()

    def _lib_status(self, text):
        sm = self.root.ids.sm
        if "library" in sm.screen_names:
            sm.get_screen("library").status_text = text